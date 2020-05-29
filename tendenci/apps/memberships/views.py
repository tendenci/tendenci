from builtins import str
import os
import math
from decimal import Decimal
from hashlib import md5
#from dateutil.parser import parse
from datetime import datetime, timedelta, date
import time as ttime
import subprocess
import calendar
from collections import OrderedDict
from dateutil.relativedelta import relativedelta

from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.db.models.fields import AutoField
from django.utils.encoding import smart_str
import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.db.models import ForeignKey, OneToOneField
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.urls.resolvers import NoReverseMatch

#from geraldo.generators import PDFGenerator

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.libs.utils import python_executable
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.base.http import Http403
from tendenci.apps.base.decorators import password_required
from tendenci.apps.base.utils import send_email_notification
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.corporate_memberships.models import (CorpMembership,
                                                          CorpProfile,
                                                          CorpMembershipApp,
                                                          IndivEmailVerification)
#from .reports import ReportNewMems
from tendenci.apps.exports.utils import render_csv
from tendenci.apps.perms.utils import get_notice_recipients

from tendenci.apps.discounts.models import Discount, DiscountUse
from tendenci.apps.discounts.utils import assign_discount
from tendenci.apps.profiles.models import Profile
from tendenci.apps.memberships.models import (
    MembershipType, Notice, MembershipImport, MembershipDefault, MembershipSet,
    MembershipImportData, MembershipApp, MembershipAppField)
from tendenci.apps.memberships.forms import (
    MembershipExportForm, AppCorpPreForm, MembershipDefaultForm,
    ReportForm, MembershipDefaultUploadForm, UserForm, ProfileForm,
    EducationForm,
    DemographicsForm,
    MembershipDefault2Form,
    AutoRenewSetupForm)
from tendenci.apps.memberships.utils import (prepare_chart_data,
    get_days, get_over_time_stats,
    get_membership_stats, ImportMembDefault,
    get_membership_app, get_membership_summary_data)
from tendenci.apps.base.forms import CaptchaForm
from tendenci.apps.perms.decorators import is_enabled


def membership_index(request):
    if request.user.profile:
        if request.user.profile.is_superuser or request.user.profile.is_staff:
            return HttpResponseRedirect(reverse('membership.application_entries_search'))
    return HttpResponseRedirect(reverse('membership.search'))


def membership_search(request, template_name="memberships/search.html"):
    #membership_view_perms = get_setting('module', 'memberships', 'memberprotection')

    #if not membership_view_perms == "public":
    return HttpResponseRedirect(reverse('profile.search') + "?member_only=on")


@is_enabled('memberships')
@login_required
def membership_details(request, id=0, template_name="memberships/details.html"):
    """
    Membership details.
    """
    membership = get_object_or_404(MembershipDefault, pk=id)

    member_can_edit_records = get_setting('module', 'memberships', 'member_edit')

    has_approve_perm = has_perm(request.user, 'memberships.approve_membershipdefault') and \
                has_perm(request.user, 'memberships.change_membershipdefault')
    
    # allow only superuser, or owner or users with the approve permission to view this page
    if not any((request.user.profile.is_superuser,
            request.user == membership.user,
            has_approve_perm)):
        raise Http403

    if request.user.profile.is_superuser or has_approve_perm:
        GET_KEYS = request.GET

        if 'approve' in GET_KEYS:
            is_renewal = membership.is_renewal()
            membership.approve(request_user=request.user)
            membership.send_email(request, ('approve_renewal' if is_renewal else 'approve'))
            messages.add_message(request, messages.SUCCESS, _('Successfully Approved'))

        if 'disapprove' in GET_KEYS:
            membership.disapprove(request_user=request.user)
            messages.add_message(request, messages.SUCCESS, _('Successfully Disapproved'))

        if 'expire' in GET_KEYS:
            membership.expire(request_user=request.user)
            messages.add_message(request, messages.SUCCESS, _('Successfully Expired'))

        if 'print' in GET_KEYS:
            template_name = 'memberships/details_print.html'

    # get the membership app for this membership
    app = membership.app
    if not app:
        app = get_membership_app(membership)
        # this membership is not associated with any app
        # figure out which app it belongs to

    # get the fields for the app
    app_fields = app.fields.filter(display=True)

    if not request.user.profile.is_superuser:
        app_fields = app_fields.filter(admin_only=False)

    app_fields = app_fields.order_by('position')
    app_fields = app_fields.exclude(field_name='corporate_membership_id')

    profile_form = ProfileForm(app_fields, instance=membership.user.profile)

    education_form = EducationForm(app_fields, request.POST or None, user=membership.user)

    EventLog.objects.log(instance=membership)

    return render_to_resp(
        request=request, template_name=template_name, context={
            'membership': membership,
            'profile_form': profile_form,
            'education_form': education_form,
            'member_can_edit_records' : member_can_edit_records,
            'has_approve_perm': has_approve_perm
        })


def membership_applications(request, template_name="memberships/applications/list.html"):

    apps = MembershipApp.objects.all()

    if not request.user.profile.is_superuser:
        apps = apps.filter(status_detail='published')

    if request.user.is_anonymous:
        apps = apps.filter(allow_anonymous_view=True)

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={'apps': apps})


def referer_url(request):
    """
    Save the membership-referer-url
    in sessions.  Then redirect to the 'next' URL
    """
    next = request.GET.get('next')
    site_url = get_setting('site', 'global', 'siteurl')

    if not next:
        raise Http404

    #  make referer-url relative if possible; remove domain
    if 'HTTP_REFERER' in request.META:
        referer_url = request.META['HTTP_REFERER'].split(site_url)[-1]
        request.session['membership-referer-url'] = referer_url

    try:
        return redirect(next)
    except NoReverseMatch:
        raise Http404 


def application_detail_default(request, **kwargs):
    """
    Returns default membership application response
    """

    if request.method == 'POST':
        form = MembershipDefaultForm(request.POST)

        if form.is_valid():
            membership = form.save(request=request, commit=False)

            if membership.get_invoice():

                # is online payment
                online_payment_requirements = (
                    membership.get_invoice().total > 0,
                    membership.payment_method,
                    membership.payment_method.is_online,
                )

                # online payment
                if all(online_payment_requirements):
                    return HttpResponseRedirect(reverse(
                        'payment.pay_online',
                        args=[membership.get_invoice().pk,
                            membership.get_invoice().guid]
                    ))

            # show membership edit page
            if request.user.profile.is_superuser:
                return HttpResponseRedirect(reverse(
                'admin:memberships_membershipdefault_change',
                args=[membership.pk]
                ))

            # show confirmation page
            return HttpResponseRedirect(reverse(
                'membership.application_confirmation_default',
                args=[membership.guid]
            ))

    else:

        # create default form
        form = MembershipDefaultForm(request=request)

    # show application
    return render_to_resp(
        request=request, template_name='memberships/applications/detail_default.html', context={
        'form': form,
        }
    )


def application_confirmation_default(request, hash):
    """
    Responds with default confirmation
    """
    template_name = 'memberships/applications/confirmation_default2.html'
    membership = get_object_or_404(MembershipDefault, guid=hash)
    if membership.corporate_membership_id:
        corp_app = CorpMembershipApp.objects.current_app()
        if not corp_app:
            raise Http404
        app = corp_app.memb_app
    else:
        app = membership.app

    EventLog.objects.log(instance=membership)

    return render_to_resp(
        request=request, template_name=template_name, context={
        'is_confirmation': True,
        'membership': membership,
        'app': app
        })


@login_required
def application_entries_search(request):
    """
    Redirect to the admin area membership list view.
    """
    return redirect("admin:memberships_membershipdefault_changelist")


@login_required
def notice_email_content(request, id, template_name="memberships/notices/email_content.html"):
    if not request.user.profile.is_superuser:
        raise Http403
    notice = get_object_or_404(Notice, pk=id)

    EventLog.objects.log(instance=notice)

    return render_to_resp(request=request, template_name=template_name, context={
        'notice': notice,
        })


@login_required
@password_required
def membership_default_import_upload(request,
            template_name='memberships/import_default/upload.html'):
    """
    Import memberships to the MembershipDefault
    """
    if not request.user.profile.is_superuser:
        raise Http403

    # make sure the site has membership types set up
    memb_type_exists = MembershipType.objects.all().exists()
    memb_app_exists = MembershipApp.objects.all().exists()

    form = MembershipDefaultUploadForm(request.POST or None,
                                       request.FILES or None)
    if request.method == 'POST' and memb_type_exists and memb_app_exists:
        if form.is_valid():
            memb_import = form.save(commit=False)
            memb_import.creator = request.user
            memb_import.save()

            # redirect to preview page.
            return redirect(reverse('memberships.default_import_preview',
                                     args=[memb_import.id]))

    # list of foreignkey fields
    user_fks = [field.name for field in User._meta.fields
                if isinstance(field, (ForeignKey, OneToOneField))]
    profile_fks = [field.name for field in Profile._meta.fields
                   if isinstance(field, (ForeignKey, OneToOneField))]
    memb_fks = [field.name for field in MembershipDefault._meta.fields
                if isinstance(field, (ForeignKey, OneToOneField))]

    fks = user_fks + profile_fks + memb_fks
    if 'user' in fks:
        fks.remove('user')
    fks.sort()
    foreign_keys = ', '.join(fks)

    return render_to_resp(request=request, template_name=template_name, context={
        'form': form,
        'memb_type_exists': memb_type_exists,
        'memb_app_exists': memb_app_exists,
        'foreign_keys': foreign_keys
        })


@login_required
def membership_default_import_preview(request, mimport_id,
                template_name='memberships/import_default/preview.html'):
    """
    Preview the import
    """

    if not request.user.profile.is_superuser:
        raise Http403

    #invalidate('memberships_membershipimport')
    mimport = get_object_or_404(MembershipImport, pk=mimport_id)

    if mimport.status == 'preprocess_done':

        try:
            curr_page = int(request.GET.get('page', 1))
        except:
            curr_page = 1

        num_items_per_page = 10

        total_rows = MembershipImportData.objects.filter(mimport=mimport).count()

        # if total_rows not updated, update it
        if mimport.total_rows != total_rows:
            mimport.total_rows = total_rows
            mimport.save()
        num_pages = int(math.ceil(total_rows * 1.0 / num_items_per_page))
        if curr_page <= 0 or curr_page > num_pages:
            curr_page = 1

        # calculate the page range to display if the total # of pages > 35
        # display links in 3 groups - first 10, middle 10 and last 10
        # the middle group will contain the current page.
        start_num = 35
        max_num_in_group = 10
        if num_pages > start_num:
            # first group
            page_range = list(range(1, max_num_in_group + 1))
            # middle group
            i = curr_page - int(max_num_in_group / 2)
            if i <= max_num_in_group:
                i = max_num_in_group
            else:
                page_range.extend(['...'])
            j = i + max_num_in_group
            if j > num_pages - max_num_in_group:
                j = num_pages - max_num_in_group
            page_range.extend(list(range(i, j + 1)))
            if j < num_pages - max_num_in_group:
                page_range.extend(['...'])
            # last group
            page_range.extend(list(range(num_pages - max_num_in_group,
                                         num_pages + 1)))
        else:
            page_range = list(range(1, num_pages + 1))

        # slice the data_list
        start_index = (curr_page - 1) * num_items_per_page + 2
        end_index = curr_page * num_items_per_page + 2
        if end_index - 2 > total_rows:
            end_index = total_rows + 2
        data_list = MembershipImportData.objects.filter(
                                mimport=mimport,
                                row_num__gte=start_index,
                                row_num__lt=end_index).order_by(
                                    'row_num')

        users_list = []
        #print data_list
        imd = ImportMembDefault(request.user, mimport, dry_run=True)
        # to be efficient, we only process memberships on the current page
        fieldnames = None
        for idata in data_list:
            user_display = imd.process_default_membership(idata)

            user_display['row_num'] = idata.row_num
            users_list.append(user_display)
            if not fieldnames:
                fieldnames = list(idata.row_data.keys())

        return render_to_resp(request=request, template_name=template_name, context={
            'mimport': mimport,
            'users_list': users_list,
            'curr_page': curr_page,
            'total_rows': total_rows,
            'prev': curr_page - 1,
            'next': curr_page + 1,
            'num_pages': num_pages,
            'page_range': page_range,
            'fieldnames': fieldnames,
            })
    else:
        if mimport.status in ('processing', 'completed'):
                return redirect(reverse('memberships.default_import_status',
                                     args=[mimport.id]))
        else:
            if mimport.status == 'not_started':
                subprocess.Popen([python_executable(), "manage.py",
                              "membership_import_preprocess",
                              str(mimport.pk)])

            return render_to_resp(request=request, template_name=template_name, context={
                'mimport': mimport,
                })


@login_required
def membership_default_import_process(request, mimport_id):
    """
    Process the import
    """
    if not request.user.profile.is_superuser:
        raise Http403
    #invalidate('memberships_membershipimport')
    mimport = get_object_or_404(MembershipImport,
                                    pk=mimport_id)
    if mimport.status == 'preprocess_done':
        mimport.status = 'processing'
        mimport.num_processed = 0
        mimport.save()
        # start the process
        subprocess.Popen([python_executable(), "manage.py",
                          "import_membership_defaults",
                          str(mimport.pk),
                          str(request.user.pk)])

        # log an event
        EventLog.objects.log()

    # redirect to status page
    return redirect(reverse('memberships.default_import_status',
                                     args=[mimport.id]))


@login_required
def membership_default_import_status(request, mimport_id,
                    template_name='memberships/import_default/status.html'):
    """
    Display import status
    """
    if not request.user.profile.is_superuser:
        raise Http403
    #invalidate('memberships_membershipimport')
    mimport = get_object_or_404(MembershipImport,
                                    pk=mimport_id)
    if mimport.status not in ('processing', 'completed'):
        return redirect(reverse('memberships.default_import'))

    return render_to_resp(request=request, template_name=template_name, context={
        'mimport': mimport,
        })


@login_required
def membership_default_import_download_recap(request, mimport_id):
    """
    Download import recap.
    """

    if not request.user.profile.is_superuser:
        raise Http403
    #invalidate('memberships_membershipimport')
    mimport = get_object_or_404(MembershipImport,
                                    pk=mimport_id)
    mimport.generate_recap()
    filename = os.path.split(mimport.recap_file.name)[1]

    recap_path = mimport.recap_file.name
    if default_storage.exists(recap_path):
        response = HttpResponse(default_storage.open(recap_path).read(),
                                content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        return response
    else:
        raise Http404


@csrf_exempt
@login_required
def membership_default_import_get_status(request, mimport_id):
    """
    Get the import status and return as json
    """
    if not request.user.profile.is_superuser:
        raise Http403
    #invalidate('memberships_membershipimport')
    mimport = get_object_or_404(MembershipImport,
                                    pk=mimport_id)

    status_data = {'status': mimport.status,
                   'total_rows': str(mimport.total_rows),
                   'num_processed': str(mimport.num_processed)}

    if mimport.status == 'completed':
        summary_list = mimport.summary.split(',')
        status_data['num_insert'] = summary_list[0].split(':')[1]
        status_data['num_update'] = summary_list[1].split(':')[1]
        status_data['num_update_insert'] = summary_list[2].split(':')[1]
        status_data['num_invalid'] = summary_list[3].split(':')[1]

    return HttpResponse(simplejson.dumps(status_data))


@csrf_exempt
@login_required
def membership_default_import_check_preprocess_status(request, mimport_id):
    """
    Get the import encoding status
    """
    if not request.user.profile.is_superuser:
        raise Http403
    #invalidate('memberships_membershipimport')
    mimport = get_object_or_404(MembershipImport,
                                    pk=mimport_id)

    return HttpResponse(mimport.status)


@login_required
def download_default_template(request):
    """
    Download import template for membership defaults
    """
    if not request.user.profile.is_superuser:
        raise Http403

    filename = "memberships_import_template.csv"

    title_list = [field for field in MembershipDefault._meta.fields
                     if not field.__class__ == AutoField]
    title_list = [smart_str(field.name) for field in title_list]
    # adjust the order for some fields
    title_list = title_list[14:] + title_list[:14]

    if 'sig_user_group_ids' in title_list:
        title_list.remove('sig_user_group_ids')
    # replace user field with fields in auth_user and profile
    title_list.remove('user')
    title_list = ['first_name', 'last_name', 'username', 'email', 'email2',
                  'phone', 'salutation', 'company',
                  'position_title', 'sex',  'address',
                  'address2', 'city', 'state',
                  'zipcode', 'county', 'country',
                  'address_2', 'address2_2', 'city_2', 'state_2',
                  'zipcode_2', 'county_2', 'country_2',
                  'url', 'url2', 'address_type', 'fax',
                  'work_phone', 'home_phone', 'mobile_phone',
                  'dob', 'ssn', 'spouse', 'department',
                  'school1', 'major1', 'degree1', 'graduation_year1',
                  'school2', 'major2', 'degree2', 'graduation_year2',
                  'school3', 'major3', 'degree3', 'graduation_year3',
                  'school4', 'major4', 'degree4', 'graduation_year4',
                  'ud1', 'ud2', 'ud3', 'ud4', 'ud5',
                  'ud6', 'ud7', 'ud8', 'ud9', 'ud10',
                  'ud11', 'ud12', 'ud13', 'ud14', 'ud15',
                  'ud16', 'ud17', 'ud18', 'ud19', 'ud20',
                  'ud21', 'ud22', 'ud23', 'ud24', 'ud25',
                  'ud26', 'ud27', 'ud28', 'ud29', 'ud30',
                  ] + title_list
    data_row_list = []

    return render_csv(filename, title_list,
                        data_row_list)

from tendenci.apps.memberships.utils import run_membership_export
@login_required
@password_required
def membership_default_export(
    request, template='memberships/default_export.html'):
    """
    Export memberships as .csv
    """
    try:
        cp_id = int(request.GET.get('cp_id', 0))
    except:
        cp_id = 0

    if cp_id:
        corp_profile = get_object_or_404(CorpProfile, pk=cp_id)
    else:
        corp_profile = None

    if not request.user.profile.is_superuser:
        if not (corp_profile and corp_profile.is_rep(request.user)):
            raise Http403

    form = MembershipExportForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():

            export_fields = form.cleaned_data['export_fields']
            export_type = form.cleaned_data['export_type']
            export_status_detail = form.cleaned_data['export_status_detail']

            identifier = int(ttime.time())
            run_membership_export(request, 
                          identifier=identifier,
                          export_fields=export_fields,
                          export_type=export_type,
                          export_status_detail=export_status_detail,
                          user_id=request.user.id,
                          cp_id=cp_id)

            # log an event
            EventLog.objects.log()
            status_url = reverse('memberships.default_export_status', args=[identifier])

            if cp_id:
                status_url = '%s?cp_id=%d' % (status_url, cp_id)

            return redirect(status_url)

    context = {"form": form,
               'corp_profile': corp_profile}
    return render_to_resp(request=request, template_name=template, context=context)


@login_required
@password_required
def membership_default_export_status(request, identifier,
                        template='memberships/default_export_status.html'):
    """
    Display export status.
    """
    try:
        cp_id = int(request.GET.get('cp_id', 0))
    except:
        cp_id = 0

    if cp_id:
        corp_profile = get_object_or_404(CorpProfile,
                                    pk=cp_id)
    else:
        corp_profile = None
    if not request.user.profile.is_superuser:
        if not (corp_profile and corp_profile.is_rep(request.user)):
            raise Http403

    export_path = 'export/memberships/%s_%d.csv' % (identifier, cp_id)
    download_ready = False
    if default_storage.exists(export_path):
        download_ready = True
    else:
        temp_export_path = 'export/memberships/%s_%d_temp.csv' % (
                                            identifier, cp_id)

        if not default_storage.exists(temp_export_path) and \
                not default_storage.exists(export_path):
            raise Http404

    context = {'identifier': identifier,
               'download_ready': download_ready,
               'corp_profile': corp_profile}
    return render_to_resp(request=request, template_name=template, context=context)


@csrf_exempt
@login_required
def membership_default_export_check_status(request, identifier):
    """
    Check and get the export status.
    """
    try:
        cp_id = int(request.GET.get('cp_id', 0))
    except:
        cp_id = 0
    if cp_id:
        corp_profile = get_object_or_404(CorpProfile,
                                    pk=cp_id)
    else:
        corp_profile = None

    status = ''
    if not request.user.profile.is_superuser:
        if not (corp_profile and corp_profile.is_rep(request.user)):
            raise Http403
    export_path = 'export/memberships/%s_%d.csv' % (identifier, cp_id)
    if default_storage.exists(export_path):
        status = 'done'
    return HttpResponse(status)


@login_required
@password_required
def membership_default_export_download(request, identifier):
    try:
        cp_id = int(request.GET.get('cp_id', 0))
    except:
        cp_id = 0
    if cp_id:
        corp_profile = get_object_or_404(CorpProfile,
                                    pk=cp_id)
    else:
        corp_profile = None

    if not request.user.profile.is_superuser:
        if not (corp_profile and corp_profile.is_rep(request.user)):
            raise Http403

    file_name = '%s_%s.csv' % (identifier, cp_id)
    file_path = 'export/memberships/%s' % file_name
    if not default_storage.exists(file_path):
        raise Http404

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="membership_export_%s"' % file_name
    response.content = default_storage.open(file_path).read()
    return response


@csrf_exempt
@login_required
def get_app_fields_json(request):
    """
    Get the app fields and return as json
    """
    if not request.user.profile.is_superuser:
        raise Http403

    complete_list = simplejson.loads(
        render_to_string(template_name='memberships/app_fields.json'))
    return HttpResponse(simplejson.dumps(complete_list), content_type="application/json")


@csrf_exempt
@login_required
def get_taken_fields(request):
    """
    Returns a list of json fields no longer available.
    Data type returned is JSON.
    """
    try:
        app_pk = int(request.POST.get('app_pk')) or 0
    except ValueError:
        app_pk = 0
    taken_list = MembershipAppField.objects.filter(
        Q(field_name__startswith='ud'), (Q(display=True) | Q(admin_only=True))).exclude(
            membership_app=app_pk).values_list(
                'field_name', flat=True)

    return HttpResponse(simplejson.dumps(list(taken_list)))


def membership_default_preview(
        request, slug, template='memberships/applications/preview.html'):
    """
    Membership default preview.
    """
    app = get_object_or_404(MembershipApp, slug=slug)
    is_superuser = request.user.profile.is_superuser
    app_fields = app.fields.filter(display=True)
    if not is_superuser:
        app_fields = app_fields.filter(admin_only=False)
    app_fields = app_fields.order_by('position')

    user_form = UserForm(app_fields, request=request)
    profile_form = ProfileForm(app_fields)
    education_form = EducationForm(app_fields)
    demographics_form = DemographicsForm(app_fields)
    membership_form = MembershipDefault2Form(app_fields,
                                             request_user=request.user,
                                             membership_app=app)
    #print membership_form.field_names

    context = {'app': app,
               "app_fields": app_fields,
               'user_form': user_form,
               'profile_form': profile_form,
               'education_form': education_form,
               'demographics_form': demographics_form,
               'membership_form': membership_form}
    return render_to_resp(request=request, template_name=template, context=context)


def membership_default_add_legacy(request):
    """
    Handle the legacy default add - redirect it to an app
    for non-corporate individuals.
    """
    [app] = MembershipApp.objects.filter(
                           use_for_corp=False,
                           status=True,
                           status_detail__in=['active', 'published']
                           ).order_by('id')[:1] or [None]
    if not app:
        raise Http404

    username = request.GET.get('username', u'')
    redirect_url = reverse('membership_default.add', args=[app.slug])
    if username:
        redirect_url = '%s?username=%s' % (redirect_url, username)
    return redirect(redirect_url)


@is_enabled('memberships')
def membership_default_add(request, slug='', membership_id=None,
                           template='memberships/applications/add.html', **kwargs):
    """
    Default membership application form.
    """
    from tendenci.apps.memberships.models import Notice

    user = None
    membership = None
    renewed_corp = None
    username = request.GET.get('username', u'')
    is_renewal = False

    if membership_id:
        # it's renewal - make sure they are logged in
        if not request.user.is_authenticated:
            return HttpResponseRedirect('%s?next=%s' % (reverse('auth_login'),
                                request.get_full_path()))
        membership = get_object_or_404(MembershipDefault, id=membership_id)
        if not (request.user.is_superuser or request.user == membership.user):
            raise Http403
        is_renewal = True

    membership_type_id = request.GET.get('membership_type_id', u'')
    if membership_type_id.isdigit():
        membership_type_id = int(membership_type_id)
    else:
        membership_type_id = 0

    join_under_corporate = kwargs.get('join_under_corporate', False)
    corp_membership = None
    is_corp_rep = False

    if join_under_corporate:
        corp_app = CorpMembershipApp.objects.current_app()
        if not corp_app:
            raise Http404

        app = corp_app.memb_app

        if not has_perm(request.user, 'memberships.view_app', app):
            raise Http403

        cm_id = kwargs.get('cm_id')
        if not cm_id:
            # redirect them to the corp_pre page
            redirect_url = reverse('membership_default.corp_pre_add')

            if username:
                return HttpResponseRedirect(
                    '%s?username=%s' % (redirect_url, username))
            return redirect(redirect_url)

        # check if they have verified their email or entered the secret code
        corp_membership = get_object_or_404(CorpMembership, id=cm_id)
        is_corp_rep = corp_membership.corp_profile.is_rep(request.user)

        authentication_method = corp_app.authentication_method

        if not is_renewal:
            # imv = individual membership verification
            imv_id = kwargs.get('imv_id', 0)
            imv_guid = kwargs.get('imv_guid')

            secret_hash = kwargs.get('secret_hash', '')

            is_verified = False

            if request.user.profile.is_superuser or authentication_method == 'admin':
                is_verified = True
            elif authentication_method == 'email':
                try:
                    indiv_veri = IndivEmailVerification.objects.get(
                        pk=imv_id, guid=imv_guid)
                    is_verified = indiv_veri.verified

                except IndivEmailVerification.DoesNotExist:
                    pass

            elif authentication_method == 'secret_code':
                tmp_secret_hash = md5('{secret_code}{random_string}'.format(
                                    secret_code=corp_membership.corp_profile.secret_code,
                                    random_string=request.session.get('corp_hash_random_string', '')).encode()
                                      ).hexdigest()
                if secret_hash == tmp_secret_hash:
                    is_verified = True

            if not is_verified:
                return redirect(reverse('membership_default.corp_pre_add',
                                        args=[cm_id]))
        else:
            # check if corp membership has expired or is renewed
            renewed_corp = corp_membership.get_latest_renewed()
            if corp_membership.is_expired or (membership.expire_dt >= corp_membership.expiration_dt and not renewed_corp):
                #display_msg = _("Sorry, we can't process your membership renewal at the moment.")
                return render_to_resp(request=request, template_name='memberships/applications/corp_not_renewed.html',
                    context={'app': app,
                       'corp_membership_renew_link': reverse('corpmembership.renew', args=[corp_membership.id]),
                       'corp_membership': corp_membership,
                       'is_rep': is_corp_rep,
                       'is_admin': request.user.profile.is_superuser})

        # check if this corp. has exceeded the maximum number of members allowed if applicable
        apply_cap, membership_cap, allow_above_cap, above_cap_price = corp_membership.get_cap_info()
        if apply_cap:
            if corp_membership.members_count >= membership_cap:
                if corp_membership.members_count == membership_cap:
                    # email admin and corporate reps about this corp. has reached cap
                    # only sent when cap is reached so they don't get freaked out for too many emails
                    email_sent = corp_membership.email_reps_cap_reached()
                else:
                    email_sent = False

                if not allow_above_cap:
                    reps = corp_membership.corp_profile.reps.all()
                    # give them the option to join as an individual membership
                    join_as_indiv_url = ''
                    if not is_renewal:
                        [app_for_individuals] = MembershipApp.objects.filter(
                                                    use_for_corp=False, status=True,
                                                     status_detail__in=['active', 'published']
                                                     )[:1] or [None]
                        if app_for_individuals:
                            join_as_indiv_url = reverse('membership_default.add', args=[app_for_individuals.slug])

                    return render_to_resp(request=request, template_name='memberships/applications/corp_cap_reached.html',
                                  context={'app': app,
                                   'join_as_indiv_url': join_as_indiv_url,
                                   'email_sent': email_sent,
                                   'reps': reps,
                                   'corp_membership': corp_membership,
                                   'can_view': corp_membership.allow_view_by(request.user),
                                   'view_url': corp_membership.get_absolute_url(),
                                   'upgrade_link': reverse('corpmembership.upgrade', args=[corp_membership.id]),
                                   'is_admin': request.user.profile.is_superuser})

    else:  # regular membership
        if not request.user.profile.is_superuser:
            app = get_object_or_404(MembershipApp, slug=slug, status_detail__in=['active', 'published'])
        else:
            app = get_object_or_404(MembershipApp, slug=slug)

        if not has_perm(request.user, 'memberships.view_app', app):
            raise Http403

        if app.use_for_corp:
            redirect_url = reverse('membership_default.corp_pre_add')

            if username:
                return HttpResponseRedirect(
                    '%s?username=%s' % (redirect_url, username))
            return redirect(redirect_url)

    if not (request.user.is_superuser or (join_under_corporate and is_corp_rep)):
        if request.user.is_authenticated:
            username = username or request.user.username

    allowed_users = (
        request.user.profile.is_superuser,
        join_under_corporate and is_corp_rep,
        username == request.user.username,
    )

    if is_renewal:
        user = membership.user
    else:
        if any(allowed_users) and username:
            [user] = User.objects.filter(username=username)[:1] or [None]

    if not app:
        raise Http404

    if join_under_corporate:
        app_fields = app.fields.filter(Q(display=True) | Q(
            field_name__in=['corporate_membership_id', 'payment_method']))
    else:
        app_fields = app.fields.filter(Q(display=True) | Q(
            field_name__in=['payment_method']))

    if not request.user.profile.is_superuser:
        app_fields = app_fields.filter(admin_only=False)

    app_fields = app_fields.order_by('position')
    if not join_under_corporate:
        # exclude the corp memb field if not join under corporate
        app_fields = app_fields.exclude(field_name='corporate_membership_id')

    user_form = UserForm(
        app_fields,
        request.POST or None,
        request=request,
        is_corp_rep=is_corp_rep,
        instance=user)

    if not (request.user.profile.is_superuser or is_corp_rep) and user and 'username' in user_form.fields:
        # set username as readonly field for regular logged-in users
        # we don't want them to change their username, but they can change it through profile
        user_form.fields['username'].widget.attrs['readonly'] = 'readonly'

    if join_under_corporate and not is_renewal:
        corp_profile = corp_membership.corp_profile
        if get_setting('module', 'corporate_memberships', 'defaultcorpinfotoindividual'):
            profile_initial = {
                'company': corp_profile.name,
                'address': corp_profile.address,
                'address2': corp_profile.address2,
                'city': corp_profile.city,
                'state': corp_profile.state,
                'zipcode': corp_profile.zip,
                'country': corp_profile.country,
                'work_phone': corp_profile.phone,}
        else:
            profile_initial = {
                'company': corp_profile.name,}
    else:
        profile_initial = None

    profile = user.profile if user else None
    profile_form = ProfileForm(
        app_fields,
        request.POST or None,
        instance=profile,
        initial=profile_initial
    )

    params = {
        'request_user': request.user,
        'customer': user or request.user,
        'membership_app': app,
        'join_under_corporate': join_under_corporate,
        'corp_membership': corp_membership,
        'is_renewal': is_renewal,
    }
    if is_renewal:
        params.update({'renew_from_id': membership.id})

    if join_under_corporate:
        params['authentication_method'] = authentication_method

    education_form = EducationForm(app_fields, request.POST or None, user=user)

    if user and (not is_renewal):
        [membership] = user.membershipdefault_set.filter(
            membership_type=membership_type_id).order_by('-pk')[:1] or [None]

    demographics_form = DemographicsForm(app_fields, request.POST or None, request.FILES or None, membership=membership)

    membership_initial = {}
    if membership:
        membership_initial = {
            'membership_type': membership.membership_type,
            'payment_method': membership.payment_method,
            'groups': [group.id for group in membership.groups.all()],
            'certifications': membership.certifications,
            'work_experience': membership.work_experience,
            'referral_source': membership.referral_source,
            'referral_source_other': membership.referral_source_other,
            'referral_source_member_name': membership.referral_source_member_name,
            'referral_source_member_number': membership.referral_source_member_number,
            'affiliation_member_number': membership.affiliation_member_number,
            'primary_practice': membership.primary_practice,
            'how_long_in_practice': membership.how_long_in_practice,
            'bod_dt': membership.bod_dt,
            'chapter': membership.chapter,
            'areas_of_expertise': membership.areas_of_expertise,
            'home_state': membership.home_state,
            'year_left_native_country': membership.year_left_native_country,
            'network_sectors': membership.network_sectors,
            'networking': membership.networking,
            'government_worker': membership.government_worker,
            'government_agency': membership.government_agency,
            'license_number': membership.license_number,
            'license_state': membership.license_state,
            'industry': membership.industry,
            'region': membership.region,
        }
    multiple_membership = app.allow_multiple_membership
    if membership or join_under_corporate:
        multiple_membership = False

    membership_form = MembershipDefault2Form(app_fields,
        request.POST or None, initial=membership_initial,
        multiple_membership=multiple_membership, **params)

    captcha_form = CaptchaForm(request.POST or None)
    if request.user.is_authenticated or not app.use_captcha:
        del captcha_form.fields['captcha']

    if 'discount_code' in membership_form.fields and (not app.discount_eligible or
        not Discount.has_valid_discount(model=MembershipSet._meta.model_name)):
        del membership_form.fields['discount_code']

    if request.method == 'POST':
        membership_types = request.POST.getlist('membership_type')
        post_values = request.POST.copy()
        memberships = []
        amount_list = []
        for membership_type in membership_types:
            post_values['membership_type'] = membership_type
            membership_form2 = MembershipDefault2Form(
                app_fields, post_values, initial=membership_initial, **params)

            # tuple with boolean items
            forms_validate = (
                user_form.is_valid(),
                profile_form.is_valid(),
                education_form.is_valid(),
                demographics_form.is_valid(),
                membership_form2.is_valid(),
                captcha_form.is_valid()
            )

            # form is valid
            if all(forms_validate):
                customer = user_form.save()

                if user:
                    customer.pk = user.pk
                    customer.username = user.username
                    customer.password = customer.password or user.password

                if not hasattr(customer, 'profile'):
                    Profile.objects.create_profile(customer)

                profile_form.instance = customer.profile
                profile_form.save(request_user=customer)

                education_form.save(user=customer)

                # save demographics
                demographics = demographics_form.save(commit=False)
                if hasattr(customer, 'demographics'):
                    demographics.pk = customer.demographics.pk

                demographics.user = customer
                demographics.save()

                membership = membership_form2.save(
                    request=request,
                    user=customer,
                )

                memberships.append(membership)
                amount_list.append(membership.membership_type.price)

        if memberships:

            membership_set = MembershipSet()
            invoice = membership_set.save_invoice(memberships, app)
            invoice.entity = memberships[0].entity

            discount_code = membership_form2.cleaned_data.get('discount_code', None)
            discount_amount = Decimal(0)
            discount_list = [Decimal(0) for i in range(len(amount_list))]
            if discount_code:
                [discount] = Discount.objects.filter(
                    discount_code=discount_code, apps__model=MembershipSet._meta.model_name)[:1] or [None]
                if discount and discount.available_for(1):
                    amount_list, discount_amount, discount_list, msg = assign_discount(amount_list, discount)
                    # apply discount to invoice
                    invoice.discount_code = discount_code
                    invoice.discount_amount = discount_amount
                    invoice.subtotal -= discount_amount
                    invoice.total -= discount_amount
                    invoice.balance -= discount_amount
                    invoice.save()

            if discount_code and discount:
                for dmount in discount_list:
                    if dmount > 0:
                        DiscountUse.objects.create(discount=discount, invoice=invoice)

            if app.donation_enabled:
                # check for donation
                donation_option, donation_amount = membership_form2.cleaned_data.get('donation_option_value', (None, None))
                if donation_option:
                    if donation_option == 'default':
                        donation_amount = app.donation_default_amount
                    if donation_amount > Decimal(0):
                        membership_set.donation_amount = donation_amount
                        membership_set.save()
                        invoice.subtotal += donation_amount
                        invoice.total += donation_amount
                        invoice.balance += donation_amount
                        invoice.save()

            if memberships[0].auto_renew:
                # handle auto renew discount
                auto_renew_discount = get_setting('module', 'memberships', 'autorenewdiscount')
                if auto_renew_discount and invoice.balance > auto_renew_discount:
                    invoice.discount_amount = auto_renew_discount
                    invoice.subtotal -= auto_renew_discount
                    invoice.total -= auto_renew_discount
                    invoice.balance -= auto_renew_discount
                    invoice.save()
                    

            memberships_join_notified = []
            memberships_renewal_notified = []
            notice_sent = False
            for membership in memberships:
                membership.membership_set = membership_set

                approval_required = (
                    membership.approval_required(),
                    join_under_corporate and authentication_method == 'admin')

                if any(approval_required):
                    membership.pend()
                    membership.save()  # save pending status

                    if membership.is_renewal():
                        notice_sent = Notice.send_notice(
                            request=request,
                            emails=membership.user.email,
                            notice_type='renewal',
                            membership=membership,
                            membership_type=membership.membership_type,
                        )
                        memberships_renewal_notified.append(membership)

                    else:
                        notice_sent =  Notice.send_notice(
                            request=request,
                            emails=membership.user.email,
                            notice_type='join',
                            membership=membership,
                            membership_type=membership.membership_type,
                        )
                        memberships_join_notified.append(membership)
                else:
                    is_renewal = membership.is_renewal()
                    membership.approve(request_user=customer)
                    membership.send_email(request, ('approve_renewal' if is_renewal else 'approve'))

                # application complete
                membership.application_complete_dt = datetime.now()
                membership.application_complete_user = membership.user

                # save application fields
                membership.save()
                membership.save_invoice(status_detail='tendered')
                membership.user.profile.refresh_member_number()

                # log an event
                EventLog.objects.log(instance=membership)

            # log notices
            if memberships_join_notified:
                Notice.log_notices(memberships_join_notified,
                                   notice_type='join',
                                   notice_time='attimeof'
                                   )
            if memberships_renewal_notified:
                Notice.log_notices(memberships_renewal_notified,
                                   notice_type='renewal',
                                   notice_time='attimeof'
                                   )

            # redirect: payment gateway
            if membership_set.is_paid_online():
                merchant_account = membership_form2.cleaned_data['payment_method'].machine_name
                if merchant_account in settings.MERCHANT_ACCOUNT_NAMES:
                    return HttpResponseRedirect(reverse(
                        'payment.pay_online',
                        args=[merchant_account, invoice.pk, invoice.guid]
                    ))
                else:
                    return HttpResponseRedirect(reverse(
                        'payment.pay_online',
                        args=[invoice.pk, invoice.guid]
                    ))

            # redirect: membership edit page
            if request.user.profile.is_superuser:
                if not membership.corporate_membership_id:
                    # Redirect to admin backend only if it's not for corp members
                    # For corp members, most likely they want to add more. So,
                    # they are redirected to the confirmation page with "add more" link.
                    return HttpResponseRedirect(reverse(
                        'admin:memberships_membershipdefault_change',
                        args=[memberships[0].pk],
                    ))

            # send email notification to admin
            if not notice_sent:
                recipients = get_notice_recipients(
                    'module', 'memberships',
                    'membershiprecipients')

                extra_context = {
                    'membership': membership,
                    'app': app,
                    'request': request
                }
                send_email_notification(
                    'membership_joined_to_admin',
                    recipients,
                    extra_context)

            # redirect: confirmation page
            return HttpResponseRedirect(reverse(
                'membership.application_confirmation_default',
                args=[memberships[0].guid]
            ))

    context = {
        'app': app,
        'app_fields': app_fields,
        'user_form': user_form,
        'profile_form': profile_form,
        'education_form': education_form,
        'demographics_form': demographics_form,
        'membership_form': membership_form,
        'captcha_form': captcha_form,
        'is_edit': False,
    }
    return render_to_resp(request=request, template_name=template, context=context)


@login_required
def membership_default_edit(request, id, template='memberships/applications/add.html', **kwargs):
    """
    Default membership application form for editing the membership entries.
    """
    member_can_edit_records = get_setting('module', 'memberships', 'member_edit')

    if not member_can_edit_records:
        raise Http404

    membership = get_object_or_404(MembershipDefault, pk=id)
    is_owner = request.user == membership.user
    user = membership.user

    if not has_perm(request.user, 'memberships.change_membershipdefault', membership) and not is_owner:
        raise Http403

    app = membership.app

    if not has_perm(request.user, 'memberships.view_app', app) and not is_owner:
        raise Http403

    if not app:
        raise Http404

    # get the fields for the app
    app_fields = app.fields.filter(display=True)

    if not request.user.profile.is_superuser:
        app_fields = app_fields.filter(admin_only=False)

    app_fields = app_fields.order_by('position')

    app_fields = app_fields.exclude(field_name='corporate_membership_id')

    user_form = UserForm(
        app_fields,
        request.POST or None,
        request=request,
        instance=user)

    profile_form = ProfileForm(
        app_fields,
        request.POST or None,
        instance=user.profile
    )

    params = {
        'request_user': request.user,
        'customer': user or request.user,
        'membership_app': app,
        'edit_mode': True,
    }

    education_form = EducationForm(app_fields, request.POST or None, user=user or request.user)

    demographics_form = DemographicsForm(
        app_fields,
        request.POST or None,
        request.FILES or None,
        request=request,
        membership=membership
    )

    membership_form2 = MembershipDefault2Form(app_fields,
        request.POST or None, instance=membership,
        multiple_membership=False, **params)

    if request.method == 'POST':
        post_values = request.POST.copy()
        post_values['membership_type'] = membership.membership_type.pk

        membership_form2 = MembershipDefault2Form(app_fields,
        post_values, instance=membership,
        multiple_membership=False, **params)

        # tuple with boolean items
        forms_validate = (
            user_form.is_valid(),
            profile_form.is_valid(),
            education_form.is_valid(),
            demographics_form.is_valid(),
            membership_form2.is_valid()
        )

        if all(forms_validate):
            customer = user_form.save()

            if user:
                customer.pk = user.pk
                customer.username = user.username
                customer.password = customer.password or user.password

            if not hasattr(customer, 'profile'):
                Profile.objects.create_profile(customer)

            profile_form.instance = customer.profile
            profile_form.save(request_user=customer)

            education_form.save(user=customer)

            # save demographics
            demographics = demographics_form.save(commit=False)
            if hasattr(customer, 'demographics'):
                demographics.pk = customer.demographics.pk

            demographics.user = customer
            demographics.save()

            membership = membership_form2.save(
                request=request,
                user=customer,
            )

            membership.save()

            # log an event
            EventLog.objects.log(instance=membership)

            # redirect: membership edit page
            messages.success(request, _('Successfully updated Membership Information.'))
            return redirect(reverse('membership.details', kwargs={'id': membership.id}))

    context = {
        'app': app,
        'app_fields': app_fields,
        'user_form': user_form,
        'profile_form': profile_form,
        'education_form': education_form,
        'demographics_form': demographics_form,
        'membership_form': membership_form2,
        'is_edit': True,
        'membership' : membership
    }
    return render_to_resp(request=request, template_name=template, context=context)


@login_required
def memberships_auto_renew_setup(request, user_id, template='memberships/auto_renew_setup.html', **kwargs):
    u = get_object_or_404(User, pk=user_id)
    is_owner = request.user == u

    if not has_perm(request.user, 'memberships.change_membershipdefault') and not is_owner:
        raise Http403

    memberships = MembershipDefault.objects.filter(user=u).filter(status=True
                    ).filter(status_detail__in=['active', 'expired', 'pending']
                             ).exclude(expire_dt__isnull=True).order_by('-expire_dt')
    # exclude corp individuals
    memberships = memberships.filter(Q(corporate_membership_id=0) | Q(corporate_membership_id__isnull=True))
    if not memberships:
        raise Http404

    form = AutoRenewSetupForm(request.POST or None, memberships=memberships)

    ct = ContentType.objects.get_for_model(MembershipDefault)
    [rp] = u.recurring_payments.filter(object_content_type=ct,
                                       status=True,
                                       status_detail__in=['active', 'disabled'])[:1] or [None]
    if not rp:
        kwargs = {'platform': 'stripe', }
        rp = memberships[0].get_or_create_rp(request.user, **kwargs)
        if not rp:
            raise Http404

    if rp.status_detail == 'disabled':
        rp.status_detail = 'active'
        rp.save()

    if request.method == "POST":
        if form.is_valid():
            selected_ids = [int(id) for id in form.cleaned_data['selected_m']]
            if "cancel_auto_renew" in request.POST:
                # cancel auto renew for the selected memberships
                for m in memberships:
                    if m.id in selected_ids:
                        if m.auto_renew:
                            m.auto_renew = False
                            m.save()
            else:
                for m in memberships:
                    if m.id in selected_ids:
                        if not m.auto_renew:
                            m.auto_renew = True
                            m.save()

            msg_string = 'Updated Successfully'
            messages.add_message(request, messages.SUCCESS, _(msg_string))

    auto_renew_all_on = True
    auto_renew_all_off = True
    for m in memberships:
        if not m.auto_renew:
            auto_renew_all_on = False
        else:
            auto_renew_all_off = False

    context = {
        'memberships' : memberships,
        'u': u,
        'rp': rp,
        'source_data': rp.get_source_data(),
        'form': form,
        'is_owner': is_owner,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        'auto_renew_all_on': auto_renew_all_on,
        'auto_renew_all_off': auto_renew_all_off
    }
    return render_to_resp(request=request, template_name=template, context=context)


def membership_default_corp_pre_add(request, cm_id=None,
                    template_name="memberships/applications/corp_pre_add.html"):

    corp_app = CorpMembershipApp.objects.current_app()

    if not hasattr(corp_app, 'memb_app'):
        raise Http404

    app = corp_app.memb_app
    if not app:
        raise Http404

    form = AppCorpPreForm(request.POST or None)
    if request.user.profile.is_superuser or \
        corp_app.authentication_method == 'admin':
        del form.fields['secret_code']
        del form.fields['email']

        from .utils import get_corporate_membership_choices
        cm_choices = get_corporate_membership_choices()
        form.fields['corporate_membership_id'].choices = cm_choices

        if cm_id:
            form.fields['corporate_membership_id'].initial = cm_id
        form.auth_method = 'corporate_membership_id'

    elif corp_app.authentication_method == 'email':
        del form.fields['corporate_membership_id']
        del form.fields['secret_code']
        form.auth_method = 'email'
    else:  # secret_code
        del form.fields['corporate_membership_id']
        del form.fields['email']
        form.auth_method = 'secret_code'

    if request.method == "POST":
        if form.is_valid():
            # find the corporate_membership_id and redirect to membership add
            if form.auth_method == 'corporate_membership_id':
                corporate_membership_id = form.cleaned_data['corporate_membership_id']
            else:
                corporate_membership_id = form.corporate_membership_id

                if form.auth_method == 'email':
                    corp_memb = CorpMembership.objects.get(pk=corporate_membership_id)
                    corp_profile = corp_memb.corp_profile
                    try:
                        indiv_veri = IndivEmailVerification.objects.get(
                                    corp_profile=corp_profile,
                                    verified_email=form.cleaned_data['email'])
                        if indiv_veri.verified:
                            is_verified = True
                        else:
                            is_verified = False
                    except IndivEmailVerification.DoesNotExist:
                        is_verified = False
                        indiv_veri = IndivEmailVerification()
                        indiv_veri.corp_profile = corp_profile
                        indiv_veri.verified_email = form.cleaned_data['email']
                        if request.user and not request.user.is_anonymous:
                            indiv_veri.creator = request.user
                        indiv_veri.save()

                    # send an email to the user to verify the email address
                    # then redirect them to the verification conf page
                    # they'll need to follow the instruction in the email
                    # to continue to sign up.
                    if not is_verified:
                        recipients = [indiv_veri.verified_email]
                        extra_context = {
                            'object': indiv_veri,
                            'app': app,
                            'corp_memb': corp_memb,
                            'request': request,
                        }
                        send_email_notification(
                            'membership_corp_indiv_verify_email',
                            recipients,
                            extra_context)

                        return redirect(reverse('membership.email__to_verify_conf'))
                    else:
                        # the email address is verified
                        return redirect(reverse('membership_default.add_via_corp_domain',
                                                args=[
                                                corp_memb.id,
                                                indiv_veri.pk,
                                                indiv_veri.guid]))
                if form.auth_method == 'secret_code':
                    # secret code hash
                    random_string = User.objects.make_random_password(
                                    length=4,
                                    allowed_chars='abcdefghjkmnpqrstuvwxyz')
                    request.session['corp_hash_random_string'] = random_string
                    secret_code = form.cleaned_data['secret_code']
                    secret_hash = md5(('%s%s' % (secret_code, random_string)).encode()).hexdigest()
                    return redirect(reverse('membership.add_via_corp_secret_code',
                                            args=[
                                                corporate_membership_id,
                                                secret_hash]))

            passed_username = request.POST.get('username', u'')
            redirect_url = reverse('membership_default.add_under_corp', args=[corporate_membership_id])

            if passed_username:
                return HttpResponseRedirect('%s?username=%s' % (redirect_url, passed_username))
            return redirect(redirect_url)

    c = {'app': app, "form": form}

    return render_to_resp(request=request, template_name=template_name,
        context=c)


def email_to_verify_conf(request,
        template_name="memberships/applications/email_to_verify_conf.html"):
    return render_to_resp(request=request, template_name=template_name)


def verify_email(request,
                 id=0,
                 guid=None,
                 template_name="memberships/applications/verify_email.html"):
    indiv_veri = get_object_or_404(IndivEmailVerification, id=id, guid=guid)
    if not indiv_veri.verified:
        indiv_veri.verified = True
        indiv_veri.verified_dt = datetime.now()
        if request.user and not request.user.is_anonymous:
            indiv_veri.updated_by = request.user
        indiv_veri.save()
    corp_membership = indiv_veri.corp_profile.active_corp_membership
    if not corp_membership:
        raise Http404
    # let them continue to sign up for membership
    return redirect(reverse('membership_default.add_via_corp_domain',
                            args=[corp_membership.id,
                                  indiv_veri.pk,
                                  indiv_veri.guid]))

@login_required
def delete(request, id, template_name="memberships/applications/delete.html"):
    membership = get_object_or_404(MembershipDefault, pk=id)

    # check permission - only admin and corp rep can delete
    if not request.user.is_superuser:
        corp_profile = membership.get_corporate_profile()
        is_corp_rep = corp_profile.is_rep(request.user)
        if not is_corp_rep:
            raise Http403

    msg_deleted = ''

    if request.method == "POST":
        # reassign owner to current user
        membership.owner = request.user
        membership.owner_username = request.user.username
        membership.save()
        msg_deleted = '%s has been deleted.' % str(membership)
        membership.delete(log=True)
        messages.add_message(request, messages.SUCCESS, _(msg_deleted))

        next_page = request.GET.get('next', '')
        if next_page:
            return HttpResponseRedirect(next_page)

    return render_to_resp(
        request=request, template_name=template_name, context={
            'membership': membership,
            'msg_deleted': msg_deleted
        })


@login_required
def expire(request, id, template_name="memberships/applications/expire.html"):
    membership = get_object_or_404(MembershipDefault, pk=id)
    if membership.is_expired():
        raise Http404

    # check permission - only admin and corp rep can delete
    if not request.user.is_superuser:
        corp_profile = membership.get_corporate_profile()
        is_corp_rep = corp_profile.is_rep(request.user)
        if not is_corp_rep:
            raise Http403

    msg_expired = ''

    if request.method == "POST":
        membership.expire(request_user=request.user)
        msg_expired = '%s has been expired.' % str(membership)
        messages.add_message(request, messages.SUCCESS, _(msg_expired))

        # log an event
        EventLog.objects.log(instance=membership, description=msg_expired)

        next_page = request.GET.get('next', '')
        if next_page:
            return HttpResponseRedirect(next_page)

    return render_to_resp(
        request=request, template_name=template_name, context={
            'membership': membership,
            'msg_expired': msg_expired
        })


@staff_member_required
def membership_join_report(request):
    TODAY = date.today()
    memberships = MembershipDefault.objects.filter(status=True,
                                                   status_detail__in=["active", 'archive'])
    membership_type = u''
    membership_status = u''
    start_date = u''
    end_date = u''

    start_date = TODAY - relativedelta(months=1)
    end_date = TODAY

    if request.method == 'POST':
        form = ReportForm(request.POST)

        if form.is_valid():

            membership_type = form.cleaned_data.get('membership_type', u'')
            membership_status = form.cleaned_data.get('membership_status', u'')
            start_date = form.cleaned_data.get('start_date', u'')
            end_date = form.cleaned_data.get('end_date', u'')

            if membership_type:
                memberships = memberships.filter(membership_type=membership_type)

            if membership_status:
                memberships = memberships.filter(status_detail=membership_status)
    else:
        form = ReportForm(initial={
            'start_date': start_date.strftime('%m/%d/%Y'),
            'end_date': end_date.strftime('%m/%d/%Y')})

    end_date_time = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
    memberships = memberships.filter(application_approved_dt__gte=start_date,
                                     application_approved_dt__lt=end_date_time)
    memberships = memberships.filter(renewal=False).distinct('user__id', 'membership_type__id')

    EventLog.objects.log()

    return render_to_resp(
        request=request, template_name='reports/membership_joins.html', context={
        'membership_type': membership_type,
        'membership_status': membership_status,
        'start_date': start_date,
        'end_date': end_date,
        'memberships': memberships,
        'form': form,
        })


# See the comments in reports.py
#@staff_member_required
#def membership_join_report_pdf(request):
#    TODAY = date.today()
#    mem_type = request.GET.get('mem_type', u'')
#    mem_stat = request.GET.get('mem_stat', u'')
#    start_date = request.GET.get('start_date', u'')
#    end_date = request.GET.get('end_date', u'')
#
#    mems = MembershipDefault.objects.all()
#
#    if mem_type:
#        mems = mems.filter(membership_type=mem_type)
#
#    if mem_stat:
#        mems = mems.filter(status_detail=mem_stat.lower())
#
#    if start_date:
#        start_date = parse(start_date)  # make date object
#    else:
#        start_date = TODAY - timedelta(days=30)
#
#    if end_date:
#        end_date = parse(end_date)  # make date object
#    else:
#        end_date = TODAY
#
#    mems = mems.filter(
#        join_dt__gte=start_date, join_dt__lte=end_date).order_by('join_dt')
#
#    if not mems:
#        raise Http404
#
#    report = ReportNewMems(queryset=mems)
#    response = HttpResponse(content_type='application/pdf')
#    report.generate_by(PDFGenerator, filename=response)
#
#    EventLog.objects.log()
#
#    return response


@staff_member_required
def report_list(request, template_name='reports/membership_report_list.html'):
    """ List of all available membership reports.
    """

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name)


@staff_member_required
def report_active_members(request, template_name='reports/membership_list.html'):
    if request.GET.get('days'):
        days = int(request.GET.get('days'))
        compare_dt = datetime.now() - timedelta(days=days)
        mems = MembershipDefault.objects.filter(status=True, status_detail="active", join_dt__gte=compare_dt).order_by('join_dt')
    else:
        days = 0
        mems = MembershipDefault.objects.filter(status=True, status_detail='active')

    # sort order of all fields for the upcoming response
    is_ascending_username = True
    is_ascending_full_name = True
    is_ascending_email = True
    is_ascending_type = True
    is_ascending_subscription = True
    is_ascending_expiration = True
    is_ascending_invoice = True

    # get sort order
    sort = request.GET.get('sort', 'subscribe_dt')
    if sort == 'username':
        mems = mems.order_by('user__username')
        is_ascending_username = False
    elif sort == '-username':
        mems = mems.order_by('-user__username')
        is_ascending_username = True
    elif sort == 'full_name':
        mems = mems.order_by('user__first_name', 'user__last_name')
        is_ascending_full_name = False
    elif sort == '-full_name':
        mems = mems.order_by('-user__first_name', '-user__last_name')
        is_ascending_full_name = True
    elif sort == 'email':
        mems = mems.order_by('user__email')
        is_ascending_email = False
    elif sort == '-email':
        mems = mems.order_by('-user__email')
        is_ascending_email = True
    elif sort == 'type':
        mems = mems.order_by('membership_type')
        is_ascending_type = False
    elif sort == '-type':
        mems = mems.order_by('-membership_type')
        is_ascending_type = True
    elif sort == 'subscription':
        mems = mems.order_by('join_dt')
        is_ascending_subscription = False
    elif sort == '-subscription':
        mems = mems.order_by('-join_dt')
        is_ascending_subscription = True
    elif sort == 'expiration':
        mems = mems.order_by('expire_dt')
        is_ascending_expiration = False
    elif sort == '-expiration':
        mems = mems.order_by('-expire_dt')
        is_ascending_expiration = True
    elif sort == 'invoice':
        # since we need to sort by a related field with the proper
        # conditions we'll need to bring the sorting to the python level
        mems = sorted(mems, key=lambda mem: mem.get_invoice(), reverse=True)
        is_ascending_invoice = False

    elif sort == '-invoice':
        # since we need to sort by a related field with the proper
        # conditions we'll need to bring the sorting to the python level
        mems = sorted(mems, key=lambda mem: mem.get_invoice(), reverse=False)
        is_ascending_invoice = True

    EventLog.objects.log()

    # returns csv response ---------------
    ouput = request.GET.get('output', '')
    if ouput == 'csv':

        table_header = [
            'username',
            'full name',
            'email',
            'application',
            'type',
            'join',
            'expiration',
            'invoice',
        ]

        table_data = []
        for mem in mems:

            invoice_pk = u''
            if mem.get_invoice():
                invoice_pk = u'%i' % mem.get_invoice().pk

            table_data.append([
                mem.user.username,
                mem.user.get_full_name(),
                mem.user.email,
                mem.membership_type.name,
                mem.join_dt,
                mem.expire_dt,
                invoice_pk,
            ])

        return render_csv(
            'active-memberships.csv',
            table_header,
            table_data,
        )
    # ------------------------------------

    return render_to_resp(request=request, template_name=template_name, context={
            'mems': mems,
            'active': True,
            'days': days,
            'is_ascending_username': is_ascending_username,
            'is_ascending_full_name': is_ascending_full_name,
            'is_ascending_email': is_ascending_email,
            'is_ascending_type': is_ascending_type,
            'is_ascending_subscription': is_ascending_subscription,
            'is_ascending_expiration': is_ascending_expiration,
            'is_ascending_invoice': is_ascending_invoice,
            })


@staff_member_required
def report_expired_members(request, template_name='reports/membership_list.html'):
    """
    Returns an HTML report of expired members.
    """
    if request.GET.get('days'):
        days = int(request.GET.get('days'))
        compare_dt = datetime.now() - timedelta(days=days)
        mems = MembershipDefault.objects.filter(status_detail="expired", expire_dt__gte=compare_dt).order_by('expire_dt')
    else:
        days = 0
        mems = MembershipDefault.objects.filter(status_detail="expired")

    # sort order of all fields for the upcoming response
    is_ascending_username = True
    is_ascending_full_name = True
    is_ascending_email = True
    is_ascending_type = True
    is_ascending_subscription = True
    is_ascending_expiration = True
    is_ascending_invoice = True

    # get sort order
    sort = request.GET.get('sort', 'subscribe_dt')
    if sort == 'username':
        mems = mems.order_by('user__username')
        is_ascending_username = False
    elif sort == '-username':
        mems = mems.order_by('-user__username')
        is_ascending_username = True
    elif sort == 'full_name':
        mems = mems.order_by('user__first_name', 'user__last_name')
        is_ascending_full_name = False
    elif sort == '-full_name':
        mems = mems.order_by('-user__first_name', '-user__last_name')
        is_ascending_full_name = True
    elif sort == 'email':
        mems = mems.order_by('user__email')
        is_ascending_email = False
    elif sort == '-email':
        mems = mems.order_by('-user__email')
        is_ascending_email = True
    elif sort == 'type':
        mems = mems.order_by('membership_type')
        is_ascending_type = False
    elif sort == '-type':
        mems = mems.order_by('-membership_type')
        is_ascending_type = True
    elif sort == 'subscription':
        mems = mems.order_by('join_dt')
        is_ascending_subscription = False
    elif sort == '-subscription':
        mems = mems.order_by('-join_dt')
        is_ascending_subscription = True
    elif sort == 'expiration':
        mems = mems.order_by('expire_dt')
        is_ascending_expiration = False
    elif sort == '-expiration':
        mems = mems.order_by('-expire_dt')
        is_ascending_expiration = True
    elif sort == 'invoice':
        # since we need to sort by a related field with the proper
        # conditions we'll need to bring the sorting to the python level
        mems = sorted(mems, key=lambda mem: mem.get_invoice(), reverse=True)
        is_ascending_invoice = False
    elif sort == '-invoice':
        # since we need to sort by a related field with the proper
        # conditions we'll need to bring the sorting to the python level
        mems = sorted(mems, key=lambda mem: mem.get_invoice(), reverse=False)
        is_ascending_invoice = True

    EventLog.objects.log()

    # returns csv response ---------------
    ouput = request.GET.get('output', '')
    if ouput == 'csv':

        table_header = [
            'username',
            'first name',
            'last name',
            'email',
            'type',
            'join',
            'expiration',
            'invoice',
        ]

        table_data = []
        for mem in mems:

            invoice_pk = u''
            if mem.get_invoice():
                invoice_pk = u'%i' % mem.get_invoice().pk

            table_data.append([
                mem.user.username,
                mem.user.first_name,
                mem.user.last_name,
                mem.user.email,
                mem.membership_type.name,
                mem.join_dt,
                mem.expire_dt,
                invoice_pk,
            ])

        return render_csv(
            'expired-memberships.csv',
            table_header,
            table_data,
        )
    # ------------------------------------

    return render_to_resp(request=request, template_name=template_name, context={
            'mems': mems,
            'active': False,
            'days': days,
            'is_ascending_username': is_ascending_username,
            'is_ascending_full_name': is_ascending_full_name,
            'is_ascending_email': is_ascending_email,
            'is_ascending_type': is_ascending_type,
            'is_ascending_subscription': is_ascending_subscription,
            'is_ascending_expiration': is_ascending_expiration,
            'is_ascending_invoice': is_ascending_invoice,
            })


@staff_member_required
def report_members_summary(request, template_name='reports/membership_summary.html'):
    days = get_days(request)

    chart_data = prepare_chart_data(days)

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={
                'chart_data': chart_data,
                'date_range': (days[0], days[-1]),
            })


@staff_member_required
def report_members_over_time(request, template_name='reports/membership_over_time.html'):
    stats = get_over_time_stats()

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={
        'stats': stats,
    })


@staff_member_required
def report_members_stats(request, template_name='reports/membership_stats.html'):
    """Shows a report of memberships per membership type.
    """
    summary, total = get_membership_stats()

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={
        'summary': summary,
        'total': total,
        })


@staff_member_required
def report_member_roster(request, template_name='reports/membership_roster.html'):
    """ Shows membership roster. Extends base-print for easy printing.
    """
    members = MembershipDefault.objects.filter(status=1, status_detail="active").order_by('user__last_name')

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={'members': members})


@staff_member_required
def report_member_quick_list(request, template_name='reports/membership_quick_list.html'):
    """ Table view of current members fname, lname and company only.
    """
    members = MembershipDefault.objects.filter(status=1, status_detail="active").order_by('user__last_name')

    # returns csv response ---------------
    ouput = request.GET.get('output', '')
    if ouput == 'csv':

        table_header = [
            'first name',
            'last name',
            'company'
        ]

        table_data = []
        for mem in members:
            if hasattr(mem.user, 'profile'):
                company = mem.user.profile.company
            else:
                company = ''
            table_data.append([
                mem.user.first_name,
                mem.user.last_name,
                company
            ])

        return render_csv(
            'current-members-quicklist.csv',
            table_header,
            table_data,
        )
    # ------------------------------------

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={'members': members})


@staff_member_required
def report_members_by_company(request, template_name='reports/members_by_company.html'):
    """ Total current members by company.
    """
    company_list = Profile.objects.exclude(
                                Q(member_number='') |
                                Q(company='')).values_list(
                                'company',
                                flat=True
                                ).distinct().order_by('company')

    # get total number of active members for each company
    companies = []
    companies_processed = []
    for company in company_list:
        company = company.strip()
        if company.lower() in companies_processed:
            continue
        total_members = Profile.objects.filter(company__iexact=company,
                                            ).exclude(member_number=''
                                            ).count()
        company_dict = {
            'name': company,
            'total_members': total_members
        }
        companies.append(company_dict)
        companies_processed.append(company.lower())

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={'companies': companies})


@staff_member_required
def report_renewed_members(request, template_name='reports/renewed_members.html'):
    """ Table of memberships ordered by renew dt, filterable by time period between renew date and now.
    """
    if request.GET.get('days'):
        days = int(request.GET.get('days'))
    else:
        days = 30
    compare_dt = datetime.now() - timedelta(days=days)
    members = MembershipDefault.objects.filter(renewal=1, renew_dt__gte=compare_dt).order_by('renew_dt')

    # returns csv response ---------------
    ouput = request.GET.get('output', '')
    if ouput == 'csv':

        table_header = [
            'id',
            'member number',
            'last name',
            'first name',
            'email',
            'city',
            'state',
            'country',
            'renew date'
        ]

        table_data = []
        for mem in members:

            table_data.append([
                mem.id,
                mem.member_number,
                mem.user.last_name,
                mem.user.first_name,
                mem.user.email,
                mem.user.profile.city,
                mem.user.profile.state,
                mem.user.profile.country,
                mem.renew_dt
            ])

        return render_csv(
            'renewed-members.csv',
            table_header,
            table_data,
        )
    # ------------------------------------

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={'members': members, 'days': days})


@staff_member_required
def report_renewal_period_members(request, template_name='reports/renewal_period_members.html'):
    """ Table of memberships ordered by join dt, filterable by time period between join date and now.
    """
    members = []
    for member in MembershipDefault.objects.all():
        if member.can_renew():
            member_dict = {
                'member_number': member.member_number,
                'first_name': member.user.first_name,
                'last_name': member.user.last_name,
                'city': member.user.profile.city,
                'state': member.user.profile.state,
                'country': member.user.profile.country,
                'membership_type': member.membership_type,
                'expire_dt': member.expire_dt
            }
            members.append(member_dict)

    members = sorted(members, key=lambda k: k['expire_dt'])

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={'members': members})


@staff_member_required
def report_grace_period_members(request, template_name='reports/grace_period_members.html'):
    """ List of memberships that are past expiration date but status detail still = active.
    """
    members = []
    for member in MembershipDefault.objects.all():
        if member.in_grace_period():
            member_dict = {
                'member_number': member.member_number,
                'first_name': member.user.first_name,
                'last_name': member.user.last_name,
                'city': member.user.profile.city,
                'state': member.user.profile.state,
                'country': member.user.profile.country,
                'membership_type': member.membership_type,
                'expire_dt': member.expire_dt
            }
            members.append(member_dict)

    members = sorted(members, key=lambda k: k['expire_dt'])

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={'members': members})


@staff_member_required
def report_active_members_ytd(request, template_name='reports/active_members_ytd.html'):
    this_year = datetime.now().year
    years = [this_year - i for i in range(5) ]
    year_selected = request.GET.get('year', this_year)
    try:
        year_selected = int(year_selected)
    except:
        year_selected = this_year
    if year_selected < 1900 or year_selected > this_year:
        year_selected = this_year

    active_mems = MembershipDefault.objects.filter(status=True,
                                                   status_detail__in=["active", 'archive'])

    total_new = 0
    total_renew = 0

    months = []
    itermonths = iter(calendar.month_abbr)
    next(itermonths)

    for index, month in enumerate(itermonths):
        index = index + 1
        start_dt = datetime(year_selected, index, 1)
        end_dt = start_dt + relativedelta(months=1)
        members = active_mems.filter(application_approved_dt__gte=start_dt,
                                      application_approved_dt__lt=end_dt)
        new_mems = members.filter(renewal=False).distinct('user__id',
                                                          'membership_type__id'
                                                          ).count()
        renew_mems = members.filter(renewal=True).distinct('user__id',
                                                          'membership_type__id'
                                                          ).count()

        total_new += new_mems
        total_renew += renew_mems

        month_dict = {
            'name': month,
            'new_mems': new_mems,
            'renew_mems': renew_mems,
            'total_active': (new_mems + renew_mems)
        }
        months.append(month_dict)

    EventLog.objects.log()

    exclude_total = request.GET.get('exclude_total', False)
    if request.GET.get('print', False):
        template_name='reports/active_members_ytd_print.html'
    return render_to_resp(request=request, template_name=template_name,
                              context={'months': months,
                               'total_new': total_new,
                               'total_renew': total_renew,
                               'years': years,
                               'year_selected': year_selected,
                               'exclude_total': exclude_total})


@staff_member_required
def report_members_ytd_type(request, template_name='reports/members_ytd_type.html'):
    year = datetime.now().year
    years = [year, year - 1, year - 2, year - 3, year - 4]
    if request.GET.get('year'):
        year = int(request.GET.get('year'))

    types_new = OrderedDict()
    types_renew = OrderedDict()
    types_expired = OrderedDict()
    months = calendar.month_abbr[1:]

    membership_types = MembershipType.objects.all()

    for mtype in membership_types:
        mems = MembershipDefault.objects.filter(membership_type=mtype)
        types_new[mtype.name] = []
        types_renew[mtype.name] = []
        types_expired[mtype.name] = []
        itermonths = iter(calendar.month_abbr)
        next(itermonths)
        for index, month in enumerate(itermonths):
            index = index + 1
            new_mems = mems.filter(join_dt__year=year, join_dt__month=index).count()
            renew_mems = mems.filter(renew_dt__year=year, renew_dt__month=index).count()
            expired_mems = mems.filter(expire_dt__year=year, expire_dt__month=index).count()

            types_new[mtype.name].append(new_mems)
            types_renew[mtype.name].append(renew_mems)
            types_expired[mtype.name].append(expired_mems)

    totals_new = []
    totals_renew = []
    totals_expired = []
    itermonths = iter(calendar.month_abbr)
    next(itermonths)
    for index, month in enumerate(itermonths):
        index = index + 1
        new = MembershipDefault.objects.filter(join_dt__year=year, join_dt__month=index).count()
        renew = MembershipDefault.objects.filter(renew_dt__year=year, renew_dt__month=index).count()
        expired = MembershipDefault.objects.filter(expire_dt__year=year, expire_dt__month=index).count()
        totals_new.append(new)
        totals_renew.append(renew)
        totals_expired.append(expired)

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={'months': months, 'years': years, 'year': year, 'types_new': types_new, 'types_renew': types_renew, 'types_expired': types_expired, 'totals_new': totals_new, 'totals_renew': totals_renew, 'totals_expired': totals_expired})


@staff_member_required
def report_members_donated(request, template_name='reports/members_donated.html'):
    memberships = MembershipDefault.objects.filter(membership_set__donation_amount__gt=0
                                   ).values('id',
                                'user__first_name', 'user__last_name', 'user__username',
                                'membership_set__donation_amount', 'membership_set__invoice',
                                'create_dt', 'status_detail'
                                ).order_by('-membership_set__donation_amount', 'user__last_name')

    return render_to_resp(request=request, template_name=template_name,
                              context={'memberships': memberships,})

@is_enabled('memberships')
@staff_member_required
def memberships_overview(request,
                template_name='reports/overview.html'):
    """
    A  report of memberships overview.
    """
    if not request.user.profile.is_superuser:
        raise Http403

    summary, total = get_membership_summary_data()

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={
        'summary': summary,
        'total': total,
        })
