import os
import math
from datetime import datetime, date, time
import csv
import operator
from hashlib import md5
from sets import Set
import subprocess
import mimetypes

from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.encoding import smart_str
from django.utils import simplejson
from django.db.models import Q
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import Http404
from django.db.models import ForeignKey, OneToOneField
from django.db.models.fields import AutoField
from django.utils.translation import ugettext_lazy as _
from johnny.cache import invalidate

from tendenci.core.imports.utils import render_excel
from tendenci.core.exports.utils import render_csv

from tendenci.core.base.http import Http403
from tendenci.core.perms.utils import has_perm
from tendenci.core.base.decorators import password_required
from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.decorators import is_enabled

from tendenci.addons.corporate_memberships.models import (
                                            CorpMembershipApp,
                                            CorpMembershipRep,
                                            CorpMembership,
                                            CorpProfile,
                                            FreePassesStat,
                                            IndivMembershipRenewEntry,
                                            CorpMembershipAppField,
                                            CorpMembershipImport,
                                            CorpMembershipImportData,
                                          CorporateMembershipType,
                                          Creator)
from tendenci.addons.corporate_memberships.forms import (
                                         CorpMembershipForm,
                                         CorpProfileForm,
                                         FreePassesForm,
                                         CorpMembershipRenewForm,
                                         RosterSearchAdvancedForm,
                                         CorpMembershipSearchForm,
                                         CorpMembershipUploadForm,
                                         CorpExportForm,
                                         CorpMembershipRepForm,
                                         CreatorForm,
                                         CorpApproveForm,
                                         RosterSearchForm,
                                         CSVForm,
                                         )
from tendenci.addons.corporate_memberships.utils import (
                                        get_corporate_membership_type_choices,
                                         get_payment_method_choices,
                                         get_indiv_memberships_choices,
                                         corp_membership_rows,
                                         corp_membership_update_perms,
                                         get_corp_memb_summary,
                                         corp_memb_inv_add,
                                         dues_rep_emails_list,
                                         get_over_time_stats,
                                         get_summary,
                                         create_salesforce_lead)
from tendenci.addons.corporate_memberships.import_processor import CorpMembershipImportProcessor
#from tendenci.addons.memberships.models import MembershipType
from tendenci.addons.memberships.models import MembershipDefault

from tendenci.core.perms.utils import get_notice_recipients
from tendenci.core.base.utils import send_email_notification, get_salesforce_access
from tendenci.core.files.models import File
from tendenci.apps.profiles.models import Profile
#from tendenci.addons.corporate_memberships.settings import use_search_index
from tendenci.core.site_settings.utils import get_setting

@is_enabled('corporate_memberships')
@staff_member_required
def free_passes_list(request,
    template='corporate_memberships/reports/free_passes_list.html'):
    """
    List the stat of all free passes.
    """
    corp_memberships = CorpMembership.objects.filter(
                            corporate_membership_type__number_passes__gt=0
                            ).exclude(status_detail='archive'
                            ).order_by('corp_profile__name')

    context = {'corp_memberships': corp_memberships}
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
@staff_member_required
def free_passes_edit(request, id,
            template='corporate_memberships/free_passes_edit.html'):
    """
    Edit total free passes allowed for corp. membership
    """
    corp_membership = get_object_or_404(CorpMembership, id=id)
    form = FreePassesForm(request.POST or None, instance=corp_membership)
    if request.method == 'POST':
        if form.is_valid():
            corp_membership = form.save()
            # log an event
            EventLog.objects.log(instance=corp_membership)
            messages.add_message(request, messages.SUCCESS,
                    'Successfully updated free passes for %s' % corp_membership)
            # redirect to view
            return HttpResponseRedirect(reverse('corpmembership.view',
                                                args=[corp_membership.id]))

    context = {'corp_membership': corp_membership,
               'form': form}
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
@csrf_exempt
@login_required
def get_app_fields_json(request):
    """
    Get the app fields and return as json
    """
    if not request.user.profile.is_superuser:
        raise Http403

    app_fields = render_to_string('corporate_memberships/app_fields.json',
                               {}, context_instance=None)

    return HttpResponse(simplejson.dumps(simplejson.loads(app_fields)))


@is_enabled('corporate_memberships')
@login_required
def app_preview(request, slug,
                    template='corporate_memberships/applications/preview.html'):
    """
    Corporate membership application preview.
    """
    app = get_object_or_404(CorpMembershipApp, slug=slug)
    is_superuser = request.user.profile.is_superuser
    app_fields = app.fields.filter(display=True)
    if not is_superuser:
        app_fields = app_fields.filter(admin_only=False)
    app_fields = app_fields.order_by('position')

    corpprofile_form = CorpProfileForm(app_fields,
                                     request_user=request.user,
                                     corpmembership_app=app)
    corpmembership_form = CorpMembershipForm(app_fields,
                                     request_user=request.user,
                                     corpmembership_app=app)
    current_app = CorpMembershipApp.objects.current_app()
    context = {'app': app,
               'current_app': current_app,
               "app_fields": app_fields,
               'corpprofile_form': corpprofile_form,
               'corpmembership_form': corpmembership_form}
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
def corpmembership_add_pre(request,
                template='corporate_memberships/applications/add_pre.html'):
    app = CorpMembershipApp.objects.current_app()
    if not app:
        raise Http404
    form = CreatorForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            creator = form.save()
            hash = md5('%d.%s' % (creator.id, creator.email)
                       ).hexdigest()
            creator.hash = hash
            creator.save()
            # log an event
            EventLog.objects.log(instance=creator)

            # redirect to add
            return HttpResponseRedirect('%s%s' % (reverse('corpmembership.add',
                                                          args=[app.slug]),
                                              '?hash=%s' % hash))

    context = {"form": form,
               'corp_app': app}
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
def corpmembership_add(request, slug='',
                       template='corporate_memberships/applications/add.html'):
    """
    Corporate membership add.
    """
    creator = None
    hash = request.GET.get('hash', '')
    if not request.user.is_authenticated():
        if hash:
            [creator] = Creator.objects.filter(hash=hash)[:1] or [None]
        if not creator:
            # anonymous user - redirect them to enter their
            # contact email before processing
            return HttpResponseRedirect(reverse('corpmembership.add_pre'))

    if not slug:
        app = CorpMembershipApp.objects.current_app()
        if not app:
            raise Http404
    else:
        app = get_object_or_404(CorpMembershipApp, slug=slug)
        current_app = CorpMembershipApp.objects.current_app()

        if app.id != current_app.id:
            return HttpResponseRedirect(reverse('corpmembership_app.preview',
                                                args=[app.slug]))
    is_superuser = request.user.profile.is_superuser

    app_fields = app.fields.filter(display=True)
    if not is_superuser:
        app_fields = app_fields.filter(admin_only=False)
    app_fields = app_fields.exclude(field_name='expiration_dt')
    app_fields = app_fields.order_by('position')

    corpprofile_form = CorpProfileForm(app_fields,
                                     request.POST or None,
                                     request.FILES or None,
                                     request_user=request.user,
                                     corpmembership_app=app)
    corpmembership_form = CorpMembershipForm(app_fields,
                                             request.POST or None,
                                             request.FILES or None,
                                             request_user=request.user,
                                             corpmembership_app=app)
    if request.method == 'POST':
        # for free membership type, make payment method not required
        corp_memb_type_id = request.POST.get('corporate_membership_type')
        try:
            corp_memb_type_id = int(corp_memb_type_id)
        except:
            corp_memb_type_id = 0
        if corp_memb_type_id:
            try:
                corp_memb_type = CorporateMembershipType.objects.get(
                                            pk=corp_memb_type_id)
                if corp_memb_type.price <= 0:
                    corpmembership_form.fields['payment_method'].required = False
            except CorporateMembershipType.DoesNotExist:
                pass

        if all([corpprofile_form.is_valid(),
                corpmembership_form.is_valid()]):
            corp_profile = corpprofile_form.save()
            # assign a secret code for this corporate
            # secret code is a unique 6 characters long string
            corp_profile.assign_secret_code()
            corp_profile.save()
            corp_membership = corpmembership_form.save(
                                                creator=creator,
                                                corp_profile=corp_profile)

            corp_memb_type = corp_membership.corporate_membership_type
            # assign free passes
            corp_membership.total_passes_allowed = corp_memb_type.number_passes
            # calculate the expiration
            corp_membership.expiration_dt = corp_memb_type.get_expiration_dt(
                                        join_dt=corp_membership.join_dt)

            # add invoice
            inv = corp_memb_inv_add(request.user, corp_membership, app=app)
            # update corp_memb with inv
            corp_membership.invoice = inv
            corp_membership.save(log=False)

            if request.user.is_authenticated():
                # set the user as representative of the corp. membership
                CorpMembershipRep.objects.create(
                    corp_profile=corp_membership.corp_profile,
                    user=request.user,
                    is_dues_rep=True)

            # assign object permissions
            corp_membership_update_perms(corp_membership)

            # create salesforce lead if applicable
            # sf = get_salesforce_access()
            # if sf:
            #     create_salesforce_lead(sf, corp_membership.corp_profile)

            # email to user who created the corporate membership
            # include the secret code in the email
            # if authentication_method == 'secret_code'

            # send notification to user
            if creator:
                recipients = [creator.email]
            else:
                recipients = [request.user.email]
            extra_context = {
                'object': corp_membership,
                'request': request,
                'invoice': inv,
            }
            send_email_notification('corp_memb_added_user',
                                    recipients, extra_context)

            # send notification to administrators
            recipients = get_notice_recipients(
                                       'module', 'corporate_memberships',
                                       'corporatemembershiprecipients')
            extra_context = {
                'object': corp_membership,
                'request': request,
                'creator': creator
            }
            send_email_notification('corp_memb_added', recipients,
                                    extra_context)
            # log an event
            EventLog.objects.log(instance=corp_membership)
            # handle online payment
            if corp_membership.payment_method.is_online:
                if corp_membership.invoice and \
                    corp_membership.invoice.balance > 0:
                    return HttpResponseRedirect(
                                    reverse('payment.pay_online',
                                    args=[corp_membership.invoice.id,
                                          corp_membership.invoice.guid]))
            else:
                if is_superuser and corp_membership.status \
                    and corp_membership.status_detail == 'active':
                    corp_membership.approve_join(request)

            return HttpResponseRedirect(reverse('corpmembership.add_conf',
                                                args=[corp_membership.id]))

    context = {'app': app,
               "app_fields": app_fields,
               'corpprofile_form': corpprofile_form,
               'corpmembership_form': corpmembership_form}
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
def corpmembership_add_conf(request, id,
            template="corporate_memberships/applications/add_conf.html"):
    """
        Corporate membership add conf
    """
    corp_membership = get_object_or_404(CorpMembership, id=id)
    app = CorpMembershipApp.objects.current_app()

    if not app:
        raise Http404

    context = {"corporate_membership": corp_membership,
               'app': app}
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
@login_required
def corpmembership_edit(request, id,
                       template='corporate_memberships/applications/edit.html'):
    """
    Corporate membership edit.
    """
    app = CorpMembershipApp.objects.current_app()
    if not app:
        raise Http404
    corp_membership = get_object_or_404(CorpMembership, id=id)
    corp_profile = corp_membership.corp_profile
    is_superuser = request.user.profile.is_superuser

    app_fields = app.fields.filter(display=True)
    if not is_superuser:
        app_fields = app_fields.filter(admin_only=False)
    if corp_membership.is_expired:
        # if it is expired, remove the expiration_dt field so they can
        # renew this corporate membership
        app_fields = app_fields.exclude(field_name='expiration_dt')
    app_fields = app_fields.order_by('position')

    corpprofile_form = CorpProfileForm(app_fields,
                                     request.POST or None,
                                     request.FILES or None,
                                     instance=corp_profile,
                                     request_user=request.user,
                                     corpmembership_app=app)
    corpmembership_form = CorpMembershipForm(app_fields,
                                             request.POST or None,
                                             request.FILES or None,
                                             instance=corp_membership,
                                             request_user=request.user,
                                             corpmembership_app=app)

    if request.method == 'POST':
        if all([corpprofile_form.is_valid(),
                corpmembership_form.is_valid()]):
            corp_profile = corpprofile_form.save()
            corp_membership = corpmembership_form.save()

            # assign a secret code for this corporate
            # secret code is a unique 6 characters long string
            if not corp_profile.secret_code:
                corp_membership.assign_secret_code()
                corp_membership.save()

            # assign object permissions
            corp_membership_update_perms(corp_membership)

            # update salesforce lead if applicable
            # sf = get_salesforce_access()
            # if sf:
            #     create_salesforce_lead(sf, corp_membership.corp_profile)

            # send notification to administrators
            if not is_superuser:
                recipients = get_notice_recipients('module',
                                                   'corporate_membership',
                                                   'corporatemembershiprecipients')
                extra_context = {
                    'object': corp_membership,
                    'request': request,
                }
                send_email_notification('corp_memb_edited',
                                        recipients,
                                        extra_context)
            # log an event
            EventLog.objects.log(instance=corp_membership)
            # redirect to view
            return HttpResponseRedirect(reverse('corpmembership.view',
                                                args=[corp_membership.id]))

    context = {'app': app,
               "app_fields": app_fields,
               'corp_membership': corp_membership,
               'corpprofile_form': corpprofile_form,
               'corpmembership_form': corpmembership_form}
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
def corpmembership_view(request, id,
                template="corporate_memberships/applications/view.html"):
    """
        view a corporate membership
    """
    app = CorpMembershipApp.objects.current_app()
    if not app:
        raise Http404
    corp_membership = get_object_or_404(CorpMembership, id=id)
    corp_membership.status_detail = corp_membership.real_time_status_detail

    if not has_perm(request.user,
                    'corporate_memberships.view_corpmembership',
                    corp_membership):
        if not corp_membership.allow_view_by(request.user):
            raise Http403

    can_edit = False
    if has_perm(request.user,
                'corporate_memberships.change_corpmembership',
                corp_membership):
        can_edit = True

    is_superuser = request.user.profile.is_superuser

    app_fields = app.fields.filter(display=True)
    if not is_superuser:
        app_fields = app_fields.filter(admin_only=False)
    if not can_edit:
        app_fields = app_fields.exclude(field_name__in=[
                                'corporate_membership_type',
                                'payment_method',
                                'join_dt',
                                'expiration_dt',
                                'renew_dt',
                                'status',
                                'status_detail',
                                'secret_code',
                                'authorized_domain'
                                        ])
    else:
        if app.authentication_method == 'admin':
            fields_to_exclude = ['secret_code', 'authorized_domain']
        elif app.authentication_method == 'email':
            fields_to_exclude = ['secret_code']
        else:
            fields_to_exclude = ['authorized_domain']
        app_fields = app_fields.exclude(field_name__in=fields_to_exclude)

    app_fields = list(app_fields.order_by('position'))

    if can_edit:
        app_field = CorpMembershipAppField(label='Join Date',
                                            field_name='join_dt',
                                            required=True)
        app_fields.append(app_field)
        app_field = CorpMembershipAppField(label='Expiration Date',
                                            field_name='expiration_dt',
                                            required=True)
        app_fields.append(app_field)
        app_field = CorpMembershipAppField(label='Representatives',
                                    field_type='section_break',
                                    admin_only=False)
        app_fields.append(app_field)
        app_field = CorpMembershipAppField(label='Reps',
                                                field_name='reps',
                                                admin_only=False)
        app_field.value = corp_membership.corp_profile.reps
        app_fields.append(app_field)

    for app_field in app_fields:
        app_field.value = corp_membership.get_field_value(app_field.field_name)
        if app_field.field_name == 'status':
            if app_field.value:
                app_field.value = 'active'
            else:
                app_field.value = 'inactive'
        if isinstance(app_field.value, datetime) or \
                isinstance(app_field.value, date):
            app_field.is_date = True
        else:
            app_field.is_date = False
            if app_field.value is None:
                app_field.value = ''

        if len(app_field.label) < 28:
            app_field.field_div_class = 'inline-block'
            app_field.short_label = True
        else:
            app_field.field_div_class = 'block'
            app_field.short_label = False

    EventLog.objects.log(instance=corp_membership)

    # all records for this corp_profile - use to display the timeline
    if is_superuser or corp_membership.is_rep(request.user):
        all_records = CorpMembership.objects.filter(
                                corp_profile=corp_membership.corp_profile
                                ).order_by('-create_dt')
    else:
        all_records = []
    context = {"corporate_membership": corp_membership,
               'all_records': all_records,
               'app_fields': app_fields,
               'app': app,
               'user_can_edit': can_edit}
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
@login_required
def download_file(request, cm_id, field_id):
    """
    Download a user uploaded file.
    """
    corp_membership = get_object_or_404(CorpMembership, id=cm_id)
    app_field = get_object_or_404(CorpMembershipAppField, id=field_id)
    corp_profile = corp_membership.corp_profile

    if not has_perm(request.user,
                    'corporate_memberships.view_corpmembership',
                    corp_membership):
        if not corp_membership.allow_view_by(request.user):
            raise Http403
    if app_field.field_type == 'FileField':
        value = ''
        if hasattr(corp_profile, app_field.field_name):
            value = getattr(corp_profile, app_field.field_name)

            if default_storage.exists(value):
                file_name = os.path.split(value)[1]
                mimetype = mimetypes.guess_type(file_name)[0]
                if not mimetype:
                    mimetype = 'application/octet-stream'
                response = HttpResponse(default_storage.open(value).read(),
                                        mimetype=mimetype)
                response['Content-Disposition'] = 'attachment; filename=%s' % file_name
                return response

    raise Http404


@is_enabled('corporate_memberships')
def corpmembership_search(request, my_corps_only=False,
            pending_only=False,
            template_name="corporate_memberships/applications/search.html"):
    allow_anonymous_search = get_setting('module',
                                     'corporate_memberships',
                                     'anonymoussearchcorporatemembers')

    if not request.user.is_authenticated():
        if my_corps_only or not allow_anonymous_search:
            raise Http403
    is_superuser = request.user.profile.is_superuser

    # legacy pending url
    query = request.GET.get('q')
    if query == 'is_pending:true':
        pending_only = True

    if pending_only and not is_superuser:
        raise Http403

    # field names for search criteria choices
    names_list = ['name', 'address', 'city', 'state',
                   'zip', 'country', 'phone',
                   'email', 'url']

    search_form = CorpMembershipSearchForm(request.GET,
                                           names_list=names_list)
    try:
        cp_id = int(request.GET.get('cp_id'))
    except:
        cp_id = 0

    if pending_only and is_superuser:
        # pending list only for admins
        q_obj = Q(status_detail__in=['pending', 'paid - pending approval'])
        corp_members = CorpMembership.objects.filter(q_obj)
    else:
        corp_members = CorpMembership.get_my_corporate_memberships(
                                                request.user,
                                                my_corps_only=my_corps_only)
        corp_members = corp_members.exclude(status_detail='archive').order_by('corp_profile__name')

    if not corp_members.exists():
        del search_form.fields['cp_id']
    else:
        # generate the choices for the cp_id field
        corp_profiles_choices = [(0, _('Select One'))]
        for corp_memb in corp_members:
            t = (corp_memb.corp_profile.id, corp_memb.corp_profile.name)
            if not t in corp_profiles_choices:
                corp_profiles_choices.append(t)

        search_form.fields['cp_id'].choices = corp_profiles_choices

    if cp_id:
        corp_members = corp_members.filter(corp_profile_id=cp_id)

    # industry
    if 'industry' in search_form.fields:
        try:
            industry = int(request.GET.get('industry'))
        except:
            industry = 0

        if industry:
            corp_members = corp_members.filter(corp_profile__industry_id=industry)

    # corporate membership type
    if not my_corps_only and is_superuser:
        # add cm_type_id for the links in the summary report
        try:
            cm_type_id = int(request.GET.get('cm_type_id'))
        except:
            cm_type_id = 0
        if cm_type_id > 0:
            corp_members = corp_members.filter(
                        corporate_membership_type_id=cm_type_id)

    # process search criteria, search_text and search_method
    if search_form.is_valid():
        search_criteria = search_form.cleaned_data['search_criteria']
        search_text = search_form.cleaned_data['search_text']
        search_method = search_form.cleaned_data['search_method']
    else:
        search_criteria = None
        search_text = None
        search_method = None

    if search_criteria and search_text:
        search_type = '__iexact'
        if search_method == 'starts_with':
            search_type = '__istartswith'
        elif search_method == 'contains':
            search_type = '__icontains'
        if search_criteria in ['name', 'address', 'city', 'state',
                               'zip', 'country', 'phone',
                               'email', 'url']:
            search_filter = {'corp_profile__%s%s' % (search_criteria,
                                             search_type): search_text}
        else:
            search_filter = {'%s%s' % (search_criteria,
                                         search_type): search_text}

        corp_members = corp_members.filter(**search_filter)
    #corp_members = corp_members.order_by('-expiration_dt')
    corp_members = corp_members.order_by('corp_profile__name')

    EventLog.objects.log()

    return render_to_response(template_name, {
        'pending_only': pending_only,
        'corp_members': corp_members,
        'search_form': search_form},
        context_instance=RequestContext(request))


@is_enabled('corporate_memberships')
@login_required
def corpmembership_delete(request, id,
            template_name="corporate_memberships/applications/delete.html"):
    corp_memb = get_object_or_404(CorpMembership, pk=id)

    if has_perm(request.user,
                'corporate_memberships.delete_corporatemembership'):
        if request.method == "POST":
            messages.add_message(request, messages.SUCCESS,
                                 'Successfully deleted %s' % corp_memb)

            # send email notification to admin
#            if  request.user.profile.is_superuser:
#                recipients = get_notice_recipients(
#                                       'module', 'corporate_memberships',
#                                       'corporatemembershiprecipients')
#                extra_context = {
#                    'object': corp_memb,
#                    'request': request
#                }
#                send_email_notification('corp_memb_deleted', recipients,
#                                        extra_context)
            description = 'Corporate membership - %s (id=%d, corp_profile_id=%d) - deleted' % (
                                            corp_memb.corp_profile.name,
                                            corp_memb.id,
                                            corp_memb.corp_profile.id)
            EventLog.objects.log(instance=corp_memb,
                                 request=request,
                                 description=description)
            corp_memb.delete()
            # the corp_profile deletion will be handled in post_delete signal

            return HttpResponseRedirect(reverse('corpmembership.search'))

        return render_to_response(template_name, {'corp_memb': corp_memb},
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('corporate_memberships')
@login_required
def corpmembership_approve(request, id,
                template="corporate_memberships/applications/approve.html"):
    corporate_membership = get_object_or_404(CorpMembership, id=id)

    user_is_superuser = request.user.profile.is_superuser
    if not user_is_superuser:
        raise Http403

    # if not in pending, go to view page
    if not (corporate_membership.is_pending):
        return HttpResponseRedirect(reverse('corpmembership.view',
                                            args=[corporate_membership.id]))

    corp_membership_type = corporate_membership.corporate_membership_type
    if corporate_membership.renewal:
        indiv_renew_entries = corporate_membership.indivmembershiprenewentry_set.all()
        new_expiration_dt = corp_membership_type.get_expiration_dt(
                                        renewal=True,
                                        join_dt=corporate_membership.join_dt,
                                        renew_dt=corporate_membership.renew_dt)
    else:
        indiv_renew_entries = None
        new_expiration_dt = corp_membership_type.get_expiration_dt(
                                    renewal=False,
                                    join_dt=corporate_membership.join_dt)

    approve_form = CorpApproveForm(request.POST or None,
                                   corporate_membership=corporate_membership)
    if request.method == "POST":
        if approve_form.is_valid():
            msg = ''
            if 'approve' in request.POST:
                if corporate_membership.renewal:
                    # approve the renewal
                    corporate_membership.approve_renewal(request)
                    msg = """Corporate membership "%s" renewal has been APPROVED.
                        """ % corporate_membership
                else:
                    # approve join
                    params = {'create_new': True,
                              'assign_to_user': None}
                    if approve_form.fields and \
                    corporate_membership.anonymous_creator:
                        user_pk = int(approve_form.cleaned_data['users'])
                        if user_pk:
                            try:
                                params['assign_to_user'] = User.objects.get(
                                                            pk=user_pk)
                                params['create_new'] = False
                            except User.DoesNotExist:
                                pass

                    corporate_membership.approve_join(request, **params)

                    msg = """Corporate membership "%s" has been APPROVED.
                        """ % corporate_membership
            else:
                if 'disapprove' in request.POST:
                    if corporate_membership.renewal:
                        # deny the renewal
                        corporate_membership.disapprove_renewal(request)

                        msg = """Corporate membership "%s" renewal has been DENIED.
                            """ % corporate_membership
                    else:
                        # deny join
                        corporate_membership.disapprove_join(request)
                        msg = """Corporate membership "%s" has been DENIED.
                            """ % corporate_membership
            if msg:
                messages.add_message(request, messages.SUCCESS, msg)

            # assign object permissions
            corp_membership_update_perms(corporate_membership)

            EventLog.objects.log(instance=corporate_membership)

            return HttpResponseRedirect(reverse('corpmembership.view',
                                                args=[corporate_membership.id]))
    field_labels = corporate_membership.get_labels()
    context = {"corporate_membership": corporate_membership,
               'field_labels': field_labels,
               'indiv_renew_entries': indiv_renew_entries,
               'new_expiration_dt': new_expiration_dt,
               'approve_form': approve_form,
               }
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
@login_required
def corp_renew(request, id,
               template='corporate_memberships/renewal.html'):
    corp_membership = get_object_or_404(CorpMembership, id=id)

    if not has_perm(request.user,
                    'corporate_memberships.change_corpmembership',
                    corp_membership):
        if not corp_membership.allow_edit_by(request.user):
            raise Http403

    if corp_membership.is_renewal_pending:
        messages.add_message(request, messages.INFO,
                             """The corporate membership "%s"
                             has been renewed and is pending
                             for admin approval.""" % corp_membership)
        return HttpResponseRedirect(reverse('corpmembership.view',
                                        args=[corp_membership.id]))
    corpmembership_app = CorpMembershipApp.objects.current_app()
    new_corp_membership = corp_membership.copy()
    form = CorpMembershipRenewForm(
                            request.POST or None,
                            instance=new_corp_membership,
                            request_user=request.user,
                            corpmembership_app=corpmembership_app
                                   )
    if request.method == "POST":
        if form.is_valid():
            if 'update_summary' in request.POST:
                pass
            else:
                members = form.cleaned_data['members']
                # create a new corp_membership entry
                new_corp_membership = form.save()
                new_corp_membership.renewal = True
                new_corp_membership.renew_dt = datetime.now()
                new_corp_membership.status = True
                new_corp_membership.status_detail = 'pending'
                new_corp_membership.creator = request.user
                new_corp_membership.creator_username = request.user.username
                new_corp_membership.owner = request.user
                new_corp_membership.owner_username = request.user.username

                # archive old corp_memberships
                new_corp_membership.archive_old()

                # calculate the total price for invoice
                corp_memb_type = form.cleaned_data[
                                            'corporate_membership_type']
                corp_renewal_price = corp_memb_type.renewal_price
                if not corp_renewal_price:
                    corp_renewal_price = 0
                indiv_renewal_price = corp_memb_type.membership_type.renewal_price
                if not indiv_renewal_price:
                    indiv_renewal_price = 0

                renewal_total = corp_renewal_price + \
                        indiv_renewal_price * len(members)
                opt_d = {'renewal': True,
                         'renewal_total': renewal_total}
                # create an invoice
                inv = corp_memb_inv_add(request.user,
                                        new_corp_membership,
                                        **opt_d)
                new_corp_membership.invoice = inv
                new_corp_membership.save()

                EventLog.objects.log(instance=corp_membership)

                # save the individual members
                for member in members:
                    [membership] = MembershipDefault.objects.filter(id=member
                                                    )[:1] or [None]
                    if membership:
                        ind_memb_renew_entry = IndivMembershipRenewEntry(
                                        corp_membership=new_corp_membership,
                                        membership=membership,
                                        )
                        ind_memb_renew_entry.save()

                # handle online payment
                if new_corp_membership.get_payment_method().is_online:
                    if new_corp_membership.invoice \
                        and new_corp_membership.invoice.balance > 0:

                        return HttpResponseRedirect(
                                reverse('payment.pay_online',
                                    args=[new_corp_membership.invoice.id,
                                    new_corp_membership.invoice.guid]))

                # email notifications
                extra_context = {
                    'object': new_corp_membership,
                    'corp_profile': new_corp_membership.corp_profile,
                    'corpmembership_app': corpmembership_app,
                    'request': request,
                    'invoice': inv,
                }
                if request.user.is_superuser:
                    # admin: approve renewal
                    new_corp_membership.approve_renewal(request)
                else:
                    # send a notice to admin
                    recipients = get_notice_recipients(
                                           'module',
                                           'corporate_memberships',
                                           'corporatemembershiprecipients')
                    send_email_notification('corp_memb_renewed',
                                            recipients, extra_context)

                # send an email to dues reps
                recipients = dues_rep_emails_list(new_corp_membership)
                send_email_notification('corp_memb_renewed_user',
                                        recipients, extra_context)

                return HttpResponseRedirect(reverse(
                                            'corpmembership.renew_conf',
                                            args=[new_corp_membership.id]))

    summary_data = {'corp_price': 0,
                    'individual_price': 0,
                    'individual_count': 0,
                    'individual_total': 0,
                    'total_amount':0}
    if corp_membership.corporate_membership_type.renewal_price == 0:
        summary_data['individual_count'] = len(get_indiv_memberships_choices(
                                                    corp_membership))

    if request.method == "POST":
        cmt_id = request.POST.get('corporate_membership_type', 0)
        try:
            cmt = CorporateMembershipType.objects.get(id=cmt_id)
        except CorporateMembershipType.DoesNotExist:
            pass
        summary_data['individual_count'] = len(request.POST.getlist('members'))
    else:
        cmt = corp_membership.corporate_membership_type

    if cmt:
        summary_data['corp_price'] = cmt.renewal_price
        if not summary_data['corp_price']:
            summary_data['corp_price'] = 0
        summary_data['individual_price'] = cmt.membership_type.renewal_price
        if not summary_data['individual_price']:
            summary_data['individual_price'] = 0
    summary_data['individual_total'] = summary_data['individual_count'
                                        ] * summary_data['individual_price']
    summary_data['total_amount'] = summary_data['individual_total'
                                    ] + summary_data['corp_price']

    context = {"corp_membership": corp_membership,
               'corp_profile': corp_membership.corp_profile,
               'corp_app': corpmembership_app,
               'form': form,
               'summary_data': summary_data,
               }
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
def corp_renew_conf(request, id,
                    template="corporate_memberships/renewal_conf.html"):
    corp_membership = get_object_or_404(CorpMembership, id=id)

    if not has_perm(request.user,
                    'corporate_memberships.change_corporatemembership',
                    corp_membership):
        if not corp_membership.allow_view_by(request.user):
            raise Http403

    corpmembership_app = CorpMembershipApp.objects.current_app()

    EventLog.objects.log(instance=corp_membership)
    context = {"corp_membership": corp_membership,
               'corp_profile': corp_membership.corp_profile,
               'corp_app': corpmembership_app,
               }
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
@login_required
def roster_search(request,
                  template_name='corporate_memberships/roster_search.html'):
    invalidate('corporate_memberships_corpprofile')
    invalidate('corporate_memberships_corpmembership')
    form = RosterSearchAdvancedForm(request.GET or None,
                                    request_user=request.user)
    if form.is_valid():
        # cm_id - CorpMembership id
        cm_id = form.cleaned_data['cm_id']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        search_criteria = form.cleaned_data['search_criteria']
        search_text = form.cleaned_data['search_text']
        search_method = form.cleaned_data['search_method']
        active_only = form.cleaned_data['active_only']
    else:
        cm_id = None
        first_name = None
        last_name = None
        email = None
        search_criteria = None
        search_text = None
        search_method = None
        active_only = False

    if cm_id:
        [corp_membership] = CorpMembership.objects.filter(
                                    id=cm_id).exclude(
                                    status_detail='archive'
                                            )[:1] or [None]
    else:
        corp_membership = None

    memberships = MembershipDefault.objects.filter(
                        status=True
                            ).exclude(
                        status_detail='archive')

    if corp_membership:
        memberships = memberships.filter(
                    corp_profile_id=corp_membership.corp_profile.id)

    if request.user.profile.is_superuser or \
        (corp_membership and corp_membership.allow_edit_by(request.user)):
        pass
    else:
        # the function get_membership_search_filter checks for permissions
        filter_and, filter_or = CorpMembership.get_membership_search_filter(
                                                            request.user)
        q_obj = None
        if filter_and:
            q_obj = Q(**filter_and)

        if filter_or:
            q_obj_or = reduce(operator.or_,
                    [Q(**{key: value}) for key, value in filter_or.items()])
            if q_obj:
                q_obj = reduce(operator.and_, [q_obj, q_obj_or])
            else:
                q_obj = q_obj_or
        if q_obj:
            memberships = memberships.filter(q_obj)

    # check form fields - first_name, last_name and email
    filter_and = {}
    if first_name:
        filter_and.update({'user__first_name__iexact': first_name})
    if last_name:
        filter_and.update({'user__last_name__iexact': last_name})
    if email:
        filter_and.update({'user__email__iexact': email})
    if active_only:
        filter_and.update({'status_detail': 'active'})
    search_type = '__iexact'
    if search_method == 'starts_with':
        search_type = '__istartswith'
    elif search_method == 'contains':
        search_type = '__icontains'

    # check search criteria
    if search_criteria and search_text:
        if search_criteria == 'username':
            filter_and.update({'user__username%s' % search_type: search_text})
        else:
            filter_and.update({'user__profile__%s%s' % (search_criteria,
                                                        search_type
                                                        ):
                               search_text})
    if filter_and:
        memberships = memberships.filter(**filter_and)
    memberships = memberships.order_by('status_detail',
                                       'user__last_name',
                                       'user__first_name')

    if corp_membership:
        form.fields['cm_id'].initial = corp_membership.id
        EventLog.objects.log(instance=corp_membership)
    else:
        EventLog.objects.log()
    corp_profile = corp_membership and corp_membership.corp_profile

    return render_to_response(template_name, {
                                  'corp_membership': corp_membership,
                                  'corp_profile': corp_profile,
                                  'memberships': memberships,
                                  'active_only': active_only,
                                  'form': form},
            context_instance=RequestContext(request))


@is_enabled('corporate_memberships')
@login_required
@password_required
def import_upload(request,
                  template='corporate_memberships/imports/upload.html'):
    """
    Corp memberships import first step: upload
    """
    if not request.user.profile.is_superuser:
        raise Http403

    form = CorpMembershipUploadForm(request.POST or None,
                                    request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            corp_membership_import = form.save(commit=False)
            corp_membership_import.creator = request.user
            corp_membership_import.save()

            # redirect to preview page.
            return redirect(reverse('corpmembership.import_preview',
                                     args=[corp_membership_import.id]))

    # make sure the site has corp_membership types set up
    corp_memb_type_exists = CorporateMembershipType.objects.all(
                                    ).exists()

    # list of foreignkey fields
    corp_profile_fks = [field.name for field in CorpProfile._meta.fields \
                   if isinstance(field, (ForeignKey, OneToOneField))]
    corp_memb_fks = [field.name for field in CorpMembership._meta.fields \
                if isinstance(field, (ForeignKey, OneToOneField))]

    fks = Set(corp_profile_fks + corp_memb_fks)
    fks = [field for field in fks]
    if 'corp_profile' in fks:
        fks.remove('corp_profile')
    fks.sort()
    foreign_keys = ', '.join(fks)

    return render_to_response(template, {
        'form': form,
        'corp_memb_type_exists': corp_memb_type_exists,
        'foreign_keys': foreign_keys
        }, context_instance=RequestContext(request))


@is_enabled('corporate_memberships')
@login_required
def import_preview(request, mimport_id,
                template='corporate_memberships/imports/preview.html'):
    if not request.user.profile.is_superuser:
        raise Http403
    mimport = get_object_or_404(CorpMembershipImport,
                                    pk=mimport_id)

    if mimport.status == 'preprocess_done':
        try:
            curr_page = int(request.GET.get('page', 1))
        except:
            curr_page = 1
        num_items_per_page = 10
#        total_rows = len(data_list)
        total_rows = CorpMembershipImportData.objects.filter(
                                mimport=mimport).count()
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
            page_range = range(1, max_num_in_group + 1)
            # middle group
            i = curr_page - int(max_num_in_group / 2)
            if i <= max_num_in_group:
                i = max_num_in_group
            else:
                page_range.extend(['...'])
            j = i + max_num_in_group
            if j > num_pages - max_num_in_group:
                j = num_pages - max_num_in_group
            page_range.extend(range(i, j + 1))
            if j < num_pages - max_num_in_group:
                page_range.extend(['...'])
            # last group
            page_range.extend(range(num_pages - max_num_in_group,
                                    num_pages + 1))
        else:
            page_range = range(1, num_pages + 1)

        # slice the data_list
        start_index = (curr_page - 1) * num_items_per_page + 2
        end_index = curr_page * num_items_per_page + 2
        if end_index - 2 > total_rows:
            end_index = total_rows + 2
        data_list = CorpMembershipImportData.objects.filter(
                                mimport=mimport,
                                row_num__gte=start_index,
                                row_num__lt=end_index).order_by(
                                    'row_num')

        corp_membs_list = []

        imd = CorpMembershipImportProcessor(request.user, mimport, dry_run=True)
        # to be efficient, we only process corp memberships on the current page
        fieldnames = None
        for idata in data_list:
            corp_memb_display = imd.process_corp_membership(idata.row_data)
            corp_memb_display['row_num'] = idata.row_num
            corp_membs_list.append(corp_memb_display)
            if not fieldnames:
                fieldnames = idata.row_data.keys()

        return render_to_response(template, {
            'mimport': mimport,
            'corp_membs_list': corp_membs_list,
            'curr_page': curr_page,
            'total_rows': total_rows,
            'prev': curr_page - 1,
            'next': curr_page + 1,
            'num_pages': num_pages,
            'page_range': page_range,
            'fieldnames': fieldnames,
            }, context_instance=RequestContext(request))
    else:
        if mimport.status in ('processing', 'completed'):
            pass
#            return redirect(reverse('memberships.default_import_status',
#                                 args=[mimport.id]))
        else:
            if mimport.status == 'not_started':
                subprocess.Popen(["python", "manage.py",
                              "corp_membership_import_preprocess",
                              str(mimport.pk)])

            return render_to_response(template, {
                'mimport': mimport,
                }, context_instance=RequestContext(request))


@is_enabled('corporate_memberships')
@csrf_exempt
@login_required
def check_preprocess_status(request, mimport_id):
    """
    Get the import preprocessing (encoding, inserting) status
    """
    if not request.user.profile.is_superuser:
        raise Http403
    invalidate('corporate_memberships_corpmembershipimport')
    mimport = get_object_or_404(CorpMembershipImport,
                                    pk=mimport_id)

    return HttpResponse(mimport.status)


@is_enabled('corporate_memberships')
@login_required
def import_process(request, mimport_id):
    """
    Process the import
    """
    if not request.user.profile.is_superuser:
        raise Http403
    mimport = get_object_or_404(CorpMembershipImport,
                                    pk=mimport_id)
    if mimport.status == 'preprocess_done':
        mimport.status = 'processing'
        mimport.num_processed = 0
        mimport.save()
        # start the process
        subprocess.Popen(["python", "manage.py",
                          "import_corp_memberships",
                          str(mimport.pk),
                          str(request.user.pk)])

        # log an event
        EventLog.objects.log()

    # redirect to status page
    return redirect(reverse('corpmembership.import_status',
                                     args=[mimport.id]))


@is_enabled('corporate_memberships')
@login_required
def import_status(request, mimport_id,
                    template_name='corporate_memberships/imports/status.html'):
    """
    Display import status
    """
    if not request.user.profile.is_superuser:
        raise Http403
    mimport = get_object_or_404(CorpMembershipImport,
                                    pk=mimport_id)
    if mimport.status not in ('processing', 'completed'):
        return redirect(reverse('corpmembership.import'))

    return render_to_response(template_name, {
        'mimport': mimport,
        }, context_instance=RequestContext(request))


@is_enabled('corporate_memberships')
@csrf_exempt
@login_required
def import_get_status(request, mimport_id):
    """
    Get the import status and return as json
    """
    if not request.user.profile.is_superuser:
        raise Http403
    mimport = get_object_or_404(CorpMembershipImport,
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


@is_enabled('corporate_memberships')
@login_required
def download_template(request):
    """
    Download import template for  corporate memberships
    """
    from tendenci.core.perms.models import TendenciBaseModel
    if not request.user.profile.is_superuser:
        raise Http403

    filename = "corp_memberships_import_template.csv"
    base_field_list = [smart_str(field.name) for field \
                       in TendenciBaseModel._meta.fields \
                     if not field.__class__ == AutoField]
    corp_profile_field_list = [smart_str(field.name) for field \
                       in CorpProfile._meta.fields \
                     if not field.__class__ == AutoField]
    corp_profile_field_list = [name for name in corp_profile_field_list \
                               if not name in base_field_list]
    corp_profile_field_list.remove('guid')
    corp_profile_field_list.extend(['dues_rep', 'authorized_domains'])
    # change name to company_name to avoid the confusion
    corp_profile_field_list.remove('name')
    corp_profile_field_list.insert(0, 'company_name')

    corp_memb_field_list = [smart_str(field.name) for field \
                       in CorpMembership._meta.fields \
                     if not field.__class__ == AutoField]
    corp_memb_field_list = [name for name in corp_memb_field_list \
                               if not name in base_field_list]
    corp_memb_field_list.remove('guid')
    corp_memb_field_list.remove('corp_profile')
    corp_memb_field_list.remove('anonymous_creator')

    title_list = corp_profile_field_list + corp_memb_field_list \
                     + base_field_list

    return render_csv(filename, title_list, [])


@is_enabled('corporate_memberships')
@login_required
@password_required
def corpmembership_export(request,
                           template='corporate_memberships/export.html'):
    """
    Export corp memberships as .csv
    """
    from tendenci.core.perms.models import TendenciBaseModel
    if not request.user.profile.is_superuser:
        raise Http403

    form = CorpExportForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            base_field_list = [smart_str(field.name) for field \
                               in TendenciBaseModel._meta.fields \
                             if not field.__class__ == AutoField]
            corp_profile_field_list = [smart_str(field.name) for field \
                               in CorpProfile._meta.fields \
                             if not field.__class__ == AutoField]
            corp_profile_field_list = [name for name in corp_profile_field_list \
                                       if not name in base_field_list]
            corp_profile_field_list.remove('guid')
            corp_profile_field_list.append('dues_rep')
            corp_profile_field_list.append('authorized_domains')
            corp_memb_field_list = [smart_str(field.name) for field \
                               in CorpMembership._meta.fields]
                             #if not field.__class__ == AutoField]
            corp_memb_field_list.remove('guid')
            corp_memb_field_list.remove('corp_profile')
            corp_memb_field_list.remove('anonymous_creator')

            title_list = corp_profile_field_list + corp_memb_field_list

            # list of foreignkey fields
            corp_profile_fks = [field.name for field in CorpProfile._meta.fields \
                           if isinstance(field, (ForeignKey, OneToOneField))]
            corp_memb_fks = [field.name for field in CorpMembership._meta.fields \
                        if isinstance(field, (ForeignKey, OneToOneField))]

            fks = Set(corp_profile_fks + corp_memb_fks)
            #fks = [field for field in fks]

            filename = 'corporate_memberships_export.csv'
            response = HttpResponse(mimetype='text/csv')
            response['Content-Disposition'] = 'attachment; filename=' + filename

            csv_writer = csv.writer(response)

            csv_writer.writerow(title_list)
            # corp_membership_rows is a generator - for better performance
            for row_item_list in corp_membership_rows(corp_profile_field_list,
                                                      corp_memb_field_list,
                                                      fks
                                                      ):
                for i in range(0, len(row_item_list)):
                    if row_item_list[i]:
                        if isinstance(row_item_list[i], datetime):
                            row_item_list[i] = row_item_list[i].strftime('%Y-%m-%d %H:%M:%S')
                        elif isinstance(row_item_list[i], date):
                            row_item_list[i] = row_item_list[i].strftime('%Y-%m-%d')
                        elif isinstance(row_item_list[i], time):
                            row_item_list[i] = row_item_list[i].strftime('%H:%M:%S')
                        elif isinstance(row_item_list[i], basestring):
                            row_item_list[i] = row_item_list[i].encode("utf-8")
                csv_writer.writerow(row_item_list)

            # log an event
            EventLog.objects.log()
            # switch to StreamingHttpResponse once we're on 1.5
            return response
    context = {"form": form}
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
def edit_corp_reps(request, id, form_class=CorpMembershipRepForm,
                   template_name="corporate_memberships/reps/edit.html"):
    corp_memb = get_object_or_404(CorpMembership, pk=id)

    if not has_perm(request.user,
                    'corporate_memberships.change_corpmembership',
                    corp_memb):
        raise Http403

    reps = CorpMembershipRep.objects.filter(
                    corp_profile=corp_memb.corp_profile
                    ).order_by('user')
    form = form_class(corp_memb, request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            rep = form.save(commit=False)
            rep.corp_profile = corp_memb.corp_profile
            rep.save()

            corp_membership_update_perms(corp_memb)

            EventLog.objects.log(instance=rep)

            if (request.POST.get('submit', '')).lower() == 'save':
                return HttpResponseRedirect(reverse('corpmembership.view',
                                                    args=[corp_memb.id]))

    return render_to_response(template_name, {'corp_memb': corp_memb,
                                              'form': form,
                                              'reps': reps},
        context_instance=RequestContext(request))


@is_enabled('corporate_memberships')
def corp_reps_lookup(request):
    q = request.REQUEST['term']
    #use_search_index = get_setting('site', 'global', 'searchindex')
    # TODO: figure out a way of assigning search permission to dues_reps.
    use_search_index = False
    if use_search_index:
        profiles = Profile.objects.search(
                            q,
                            user=request.user
                            ).order_by('last_name_exact')
    else:
        # they don't have search index, probably just check username only
        # for the performance sake
        profiles = Profile.objects.filter(
                                 Q(user__first_name__istartswith=q) \
                               | Q(user__last_name__istartswith=q) \
                               | Q(user__username__istartswith=q) \
                               | Q(user__email__istartswith=q))
        profiles = profiles.order_by('user__last_name')

    if profiles and len(profiles) > 10:
        profiles = profiles[:10]

    if use_search_index:
        users = [p.object.user for p in profiles]
    else:
        users = [p.user for p in profiles]

    results = []
    for u in users:
        value = '%s, %s (%s) - %s' % (u.last_name, u.first_name,
                                      u.username, u.email)
        u_dict = {'id': u.id, 'label': value, 'value': value}
        results.append(u_dict)
    return HttpResponse(simplejson.dumps(results),
                        mimetype='application/json')


@is_enabled('corporate_memberships')
@login_required
def delete_corp_rep(request, id,
                    template_name="corporate_memberships/reps/delete.html"):
    rep = get_object_or_404(CorpMembershipRep, pk=id)
    corp_profile = rep.corp_profile
    corp_memb = corp_profile.corp_membership

    if corp_memb.allow_edit_by(request.user) or \
         has_perm(request.user, 'corporate_memberships.change_corpmembership'):
        if request.method == "POST":

            messages.add_message(request, messages.SUCCESS,
                                 'Successfully deleted %s' % rep)
            EventLog.objects.log()
            rep.delete()
            corp_membership_update_perms(corp_memb)

            return HttpResponseRedirect(reverse(
                                        'corpmembership.edit_corp_reps',
                                        args=[corp_memb.pk]))

        return render_to_response(template_name, {'corp_memb': corp_memb},
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('corporate_memberships')
def index(request,
          template_name="corporate_memberships/applications/index.html"):
    corp_app = CorpMembershipApp.objects.current_app()
    EventLog.objects.log()

    return render_to_response(template_name, {'corp_app': corp_app},
        context_instance=RequestContext(request))


@is_enabled('corporate_memberships')
@staff_member_required
def summary_report(request,
                template_name='corporate_memberships/reports/summary.html'):
    """
    Shows a report of corporate memberships per corporate membership type.
    """

    if not request.user.profile.is_superuser:
        raise Http403

    summary, total = get_corp_memb_summary()

    EventLog.objects.log()

    return render_to_response(template_name, {
        'summary': summary,
        'total': total,
        }, context_instance=RequestContext(request))


@is_enabled('corporate_memberships')
# TO BE DELETED
def add_pre(request, slug, template='corporate_memberships/add_pre.html'):
    corp_app = get_object_or_404(CorpApp, slug=slug)
    form = CreatorForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            creator = form.save()
            hash = md5('%d.%s' % (creator.id, creator.email)).hexdigest()
            creator.hash = hash
            creator.save()

            # redirect to add
            return HttpResponseRedirect(reverse('corp_memb.anonymous_add', args=[slug, hash]))

    context = {"form": form,
               'corp_app': corp_app}
    return render_to_response(template, context, RequestContext(request))

@is_enabled('corporate_memberships')
def add(request, slug=None, hash=None, template="corporate_memberships/add.html"):
    """
        add a corporate membership
        request.user will be set as a representative of the corporate membership.
        admin - active
        user - if paid, active, otherwise, pending
    """
    corp_app = get_object_or_404(CorpApp, slug=slug)
    user_is_superuser = request.user.profile.is_superuser

    if not user_is_superuser and corp_app.status <> 1 and corp_app.status_detail <> 'active':
        raise Http403

    creator = None
    if not request.user.is_authenticated():
#        # if app requires login and they are not logged in,
#        # prompt them to log in and redirect them back to this add page
#        messages.add_message(request, messages.INFO, 'Please log in or sign up to the site before signing up the corporate membership.')
#        return HttpResponseRedirect('%s?next=%s' % (reverse('auth_login'), reverse('corp_memb.add', args=[corp_app.slug])))
        # anonymous user - check if they have entered contact info
        if hash:
            [creator] = Creator.objects.filter(hash=hash)[:1] or [None]
        if not creator:
            # anonymous user - redirect them to enter their contact email before processing
            return HttpResponseRedirect(reverse('corp_memb.add_pre', args=[slug]))

    field_objs = corp_app.fields.filter(visible=1)
    if not user_is_superuser:
        field_objs = field_objs.filter(admin_only=0)

    field_objs = list(field_objs.order_by('position'))

    form = CorpMembForm(corp_app, field_objs, request.POST or None, request.FILES or None)

    # corporate_membership_type choices
    form.fields['corporate_membership_type'].choices = get_corporate_membership_type_choices(request.user, corp_app)

    form.fields['payment_method'].choices = get_payment_method_choices(request.user, corp_app)

    # add an admin only block for admin
    if user_is_superuser:
        field_objs.append(CorpField(label='Admin Only', field_type='section_break', admin_only=1))
        field_objs.append(CorpField(label='Join Date', field_name='join_dt', admin_only=1))
        field_objs.append(CorpField(label='Status', field_name='status', admin_only=1))
        field_objs.append(CorpField(label='status_detail', field_name='status_detail', admin_only=1))
    else:
        del form.fields['join_dt']
        del form.fields['status']
        del form.fields['status_detail']
    del form.fields['expiration_dt']

    # captcha
    #if corp_app.use_captcha and (not request.user.is_authenticated()):
    #    field_objs.append(CorpField(label='Type the code below', field_name='captcha'))
    #else:
    #    del form.fields['captcha']

    if request.method == "POST":
        if form.is_valid():
            if creator:
                corporate_membership = form.save(request.user, creator=creator)
            else:
                corporate_membership = form.save(request.user)
            if creator:
                corporate_membership.anonymous_creator = creator

            # calculate the expiration
            corp_memb_type = corporate_membership.corporate_membership_type
            corporate_membership.expiration_dt = corp_memb_type.get_expiration_dt(join_dt=corporate_membership.join_dt)

            #if corp_app.authentication_method == 'secret_code':
            # assign a secret code for this corporate
            # secret code is a unique 6 characters long string
            corporate_membership.assign_secret_code()
            corporate_membership.save()

            # generate invoice
            inv = corp_memb_inv_add(request.user, corporate_membership)
            # update corp_memb with inv
            corporate_membership.invoice = inv
            corporate_membership.save(log=False)

            if request.user.is_authenticated():
                # set the user as representative of the corp. membership
                rep = CorporateMembershipRep.objects.create(
                    corporate_membership = corporate_membership,
                    user = request.user,
                    is_dues_rep = True)

            # assign object permissions
            if not creator:
                corp_memb_update_perms(corporate_membership)

            # email to user who created the corporate membership
            # include the secret code in the email if authentication_method == 'secret_code'

            # send notification to user
            if creator:
                recipients = [creator.email]
            else:
                recipients = [request.user.email]
            extra_context = {
                'object': corporate_membership,
                'request': request,
                'invoice': inv,
            }
            send_email_notification('corp_memb_added_user', recipients, extra_context)

            # send notification to administrators
            recipients = get_notice_recipients('module', 'corporate_memberships', 'corporatemembershiprecipients')
            extra_context = {
                'object': corporate_membership,
                'request': request,
                'creator': creator
            }
            send_email_notification('corp_memb_added', recipients, extra_context)


            # handle online payment
            #if corporate_membership.payment_method.lower() in ['credit card', 'cc']:
            if corporate_membership.payment_method.is_online:
                if corporate_membership.invoice and corporate_membership.invoice.balance > 0:
                    return HttpResponseRedirect(reverse('payment.pay_online', args=[corporate_membership.invoice.id, corporate_membership.invoice.guid]))

            return HttpResponseRedirect(reverse('corp_memb.add_conf', args=[corporate_membership.id]))

    context = {"corp_app": corp_app, "field_objs": field_objs, 'form':form}
    return render_to_response(template, context, RequestContext(request))


@is_enabled('corporate_memberships')
def search(request, template_name="corporate_memberships/search.html"):
    return HttpResponseRedirect(reverse('corpmembership.search'))


@is_enabled('corporate_memberships')
def reps_lookup(request):
    q = request.REQUEST['term']
    use_search_index = get_setting('site', 'global', 'searchindex')

    if use_search_index:
        profiles = Profile.objects.search(
                            q,
                            user=request.user
                            ).order_by('last_name_exact')
    else:
        # they don't have search index, probably just check username only for performance sake
        profiles = Profile.objects.filter(Q(user__first_name__istartswith=q) \
                                       | Q(user__last_name__istartswith=q) \
                                       | Q(user__username__istartswith=q) \
                                       | Q(user__email__istartswith=q))
        profiles  = profiles.order_by('user__last_name')

    if profiles and len(profiles) > 10:
        profiles = profiles[:10]

    if use_search_index:
        users = [p.object.user for p in profiles]
    else:
        users = [p.user for p in profiles]

    results = []
    for u in users:
        value = '%s, %s (%s) - %s' % (u.last_name, u.first_name, u.username, u.email)
        u_dict = {'id': u.id, 'label': value, 'value': value}
        results.append(u_dict)
    return HttpResponse(simplejson.dumps(results),mimetype='application/json')


@is_enabled('corporate_memberships')
@staff_member_required
def new_over_time_report(request, template_name='reports/corp_mems_over_time.html'):
    """
    Shows a report of corp memberships over time.
    1 report for 1 month, 2 months, 3 months, 6 months, and 1 year
    """

    stats = get_over_time_stats()

    EventLog.objects.log()

    return render_to_response(template_name, {
        'stats':stats,
        }, context_instance=RequestContext(request))


@is_enabled('corporate_memberships')
@staff_member_required
def corp_mems_summary(request, template_name='reports/corp_mems_summary.html'):
    """
    Shows a report of corporate memberships per corporate membership type.
    """
    summary,total = get_summary()

    EventLog.objects.log()

    return render_to_response(template_name, {
        'summary':summary,
        'total':total,
        }, context_instance=RequestContext(request))
