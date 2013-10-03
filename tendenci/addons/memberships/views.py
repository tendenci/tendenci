import os
import math
import hashlib
from decimal import Decimal
from hashlib import md5
from dateutil.parser import parse
from datetime import datetime, timedelta, date
import time as ttime
import subprocess
from sets import Set
import calendar
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.db.models.fields import AutoField
from django.utils.encoding import smart_str
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.db.models import ForeignKey, OneToOneField
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from johnny.cache import invalidate
from djcelery.models import TaskMeta
from geraldo.generators import PDFGenerator
from tendenci.apps.notifications.utils import send_welcome_email

from tendenci.core.site_settings.utils import get_setting
from tendenci.core.event_logs.models import EventLog
from tendenci.core.base.http import Http403
from tendenci.core.base.decorators import password_required
from tendenci.core.base.utils import send_email_notification
from tendenci.core.perms.decorators import superuser_required
from tendenci.core.perms.utils import has_perm, update_perms_and_save, get_query_filters
from tendenci.apps.invoices.models import Invoice
from tendenci.addons.corporate_memberships.models import (CorpMembership,
                                                          CorpProfile,
                                                          CorpMembershipApp,
                                                          IndivEmailVerification,
                                                          CorporateMembership,
                                                          IndivMembEmailVeri8n)
from reports import ReportNewMems
from tendenci.core.files.models import File
from tendenci.core.exports.utils import render_csv, run_export_task
from tendenci.core.perms.utils import get_notice_recipients

from tendenci.apps.discounts.models import Discount, DiscountUse
from tendenci.apps.discounts.utils import assign_discount
from tendenci.apps.profiles.models import Profile
from tendenci.addons.memberships.models import (App, AppEntry, Membership,
    MembershipType, Notice, MembershipImport, MembershipDefault, MembershipSet,
    MembershipImportData, MembershipApp, MembershipAppField)
from tendenci.addons.memberships.forms import (
    MembershipExportForm, AppCorpPreForm, MembershipForm, MembershipDefaultForm,
    MemberApproveForm, ReportForm, EntryEditForm, ExportForm,
    AppEntryForm, MembershipDefaultUploadForm, UserForm, ProfileForm,
    DemographicsForm,
    MembershipDefault2Form)
from tendenci.addons.memberships.utils import (is_import_valid, prepare_chart_data,
    get_days, get_over_time_stats, get_status_filter,
    get_membership_stats, NoMembershipTypes, ImportMembDefault)
from tendenci.addons.memberships.importer.forms import ImportMapForm, UploadForm
from tendenci.addons.memberships.importer.utils import parse_mems_from_csv
from tendenci.addons.memberships.importer.tasks import ImportMembershipsTask
from tendenci.core.base.forms import CaptchaForm


def membership_index(request):
    if request.user.profile:
        if request.user.profile.is_superuser or request.user.profile.is_staff:
            return HttpResponseRedirect(reverse('membership.application_entries_search'))
    return HttpResponseRedirect(reverse('membership.search'))


def membership_search(request, template_name="memberships/search.html"):
    #membership_view_perms = get_setting('module', 'memberships', 'memberprotection')

    #if not membership_view_perms == "public":
    return HttpResponseRedirect(reverse('profile.search') + "?member_only=on")

    query = request.GET.get('q')
    mem_type = request.GET.get('type')
    total_count = Membership.objects.all().count()
    if get_setting('site', 'global', 'searchindex') and (total_count > 1000 or query):
        members = Membership.objects.search(query, user=request.user)
        if mem_type:
            members = members.filter(mem_type=mem_type)
        members = members.order_by('last_name')
    else:
        filters = get_query_filters(request.user, 'memberships.view_membership')
        members = Membership.objects.filter(filters).distinct()
        if mem_type:
            members = members.filter(membership_type__pk=mem_type)
        members = members.exclude(status_detail='expired')
        members = members.order_by('user__last_name')
    types = MembershipType.objects.all()

    EventLog.objects.log()

    return render_to_response(template_name, {'members': members, 'types': types},
        context_instance=RequestContext(request))


@login_required
def membership_details(request, id=0, template_name="memberships/details.html"):
    """
    Membership details.
    """
    membership = get_object_or_404(MembershipDefault, pk=id)

    super_user_or_owner = (
        request.user.profile.is_superuser,
        request.user == membership.user)

    if not any(super_user_or_owner):
        raise Http403

    if request.user.profile.is_superuser:
        GET_KEYS = request.GET.keys()

        if 'approve' in GET_KEYS:
            membership.approve(request_user=request.user)
            membership.send_email(request, 'approve')
            messages.add_message(request, messages.SUCCESS, 'Successfully Approved')

        if 'disapprove' in GET_KEYS:
            membership.disapprove(request_user=request.user)
            messages.add_message(request, messages.SUCCESS, 'Successfully Disapproved')

        if 'expire' in GET_KEYS:
            membership.expire(request_user=request.user)
            messages.add_message(request, messages.SUCCESS, 'Successfully Expired')

        if 'print' in GET_KEYS:
            template_name = 'memberships/details_print.html'

    EventLog.objects.log(instance=membership)

    return render_to_response(
        template_name, {
            'membership': membership
        }, context_instance=RequestContext(request))


@login_required
def membership_edit(request, id, form_class=MembershipForm, template_name="memberships/edit.html"):
    """
    Membership edit.
    """
    from tendenci.apps.user_groups.models import GroupMembership
    membership = get_object_or_404(Membership, pk=id)

    if not has_perm(request.user, 'memberships.change_membership', membership):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST, instance=membership, user=request.user)

        if form.is_valid():
            membership = form.save(commit=False)

            # update all permissions and save the model
            membership = update_perms_and_save(request, form, membership)

            # add or remove from group -----
            if membership.is_active():  # should be in group; make sure they're in
                membership.membership_type.group.add_user(membership.user)
            else:  # should not be in group; make sure they're out
                GroupMembership.objects.filter(
                    member=membership.user,
                    group=membership.membership_type.group
                ).delete()
            # -----

            # update member-number on profile
            membership.user.profile.refresh_member_number()

            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % membership)

            return redirect('membership.details', membership.pk)
    else:
        form = form_class(instance=membership, user=request.user)

    return render_to_response(template_name, {
        'membership': membership,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def membership_delete(request, id, template_name="memberships/delete.html"):
    """Membership delete"""
    membership = get_object_or_404(Membership, pk=id)

    if not has_perm(request.user, 'memberships.delete_membership', membership):
        raise Http403

    if request.method == "POST":

        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % membership)

        return HttpResponseRedirect(reverse('membership.search'))

    return render_to_response(template_name, {'membership': membership},
        context_instance=RequestContext(request))


def download_template(request, slug=''):
    """
    Return a csv [download response] of the application specified via slug
    """
    from tendenci.addons.memberships.utils import make_csv
    return make_csv(slug=slug)


def membership_applications(request, template_name="memberships/applications/list.html"):

    apps = MembershipApp.objects.all()

    if not request.user.profile.is_superuser:
        apps = apps.filter(status_detail='published')

    if request.user.is_anonymous():
        apps = apps.filter(allow_anonymous_view=True)

    EventLog.objects.log()

    return render(request, template_name, {'apps': apps})


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

    return redirect(next)


def application_detail_default(request, **kwargs):
    """
    Returns default membership application response
    """

    if request.method == 'POST':
        form = MembershipDefaultForm(request.POST)

        if form.is_valid():
            membership = form.save(request=request, commit=False)

            if membership.get_invoice():
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

            if request.user.profile.is_superuser:
                return HttpResponseRedirect(reverse(
                'admin:memberships_membershipdefault_change',
                args=[membership.pk]
                ))

            return HttpResponseRedirect(reverse(
                'membership.application_confirmation_default',
                args=[membership.guid]
            ))

    else:
        form = MembershipDefaultForm(request=request)

    return render_to_response(
        'memberships/applications/detail_default.html', {
        'form': form,
        }, context_instance=RequestContext(request)
    )


def application_details(request, template_name="memberships/applications/details.html", **kwargs):
    """
    Display a built membership application and handle submission.
    """
    # only allow super users to view this [old] membership form
    if not request.user.profile.is_superuser:
        raise Http404

    slug = kwargs.get('slug')
    cmb_id = kwargs.get('cmb_id')
    imv_id = kwargs.get('imv_id', 0)
    imv_guid = kwargs.get('imv_guid')
    secret_hash = kwargs.get('secret_hash', '')

    if not slug:
        raise Http404
    user = request.user

    app = get_object_or_404(App, slug=slug)
    if not app.allow_view_by(user):
        raise Http403

    # if this app is for corporation individuals, redirect them to corp-pre page if
    # they have not passed the security check.
    corporate_membership = None
    if hasattr(app, 'corp_app') and app.corp_app:
        if not cmb_id:
            # redirect them to the corp_pre page
            return redirect(reverse('membership.application_details_corp_pre', args=[app.slug]))

        corporate_membership = get_object_or_404(CorporateMembership, id=cmb_id)
        # check if they have verified their email or entered the secret code
        is_verified = False
        if request.user.profile.is_superuser or app.corp_app.authentication_method == 'admin':
            is_verified = True
        elif app.corp_app.authentication_method == 'email':
            try:
                indiv_veri = IndivMembEmailVeri8n.objects.get(pk=imv_id,
                                                              guid=imv_guid)
                if indiv_veri.verified:
                    is_verified = True
            except IndivMembEmailVeri8n.DoesNotExist:
                pass

        elif app.corp_app.authentication_method == 'secret_code':
            tmp_secret_hash = md5('%s%s' % (corporate_membership.secret_code,
                                    request.session.get('corp_hash_random_string', ''))).hexdigest()
            if secret_hash == tmp_secret_hash:
                is_verified = True

        if not is_verified:
            return redirect(reverse('membership.application_details_corp_pre', args=[slug]))

    EventLog.objects.log(instance=app)

    initial_dict = {}
    if hasattr(user, 'memberships'):
        is_only_a_member = [
            user.profile.is_superuser == False,
            user.profile.is_member == True,
        ]

        if corporate_membership:
            # exclude corp. reps, creator and owner - they should be able to add new
            is_only_a_member.append(corporate_membership.allow_edit_by(user) == False)

        if user.profile.is_superuser:
            username = request.GET.get('username', unicode())
            if username:
                try:
                    registrant = User.objects.get(username=username)
                    # get info from last time this app was filled out
                    initial_dict = app.get_initial_info(registrant)
                except:
                    pass

        elif all(is_only_a_member):
            # get info from last time this app was filled out
            initial_dict = app.get_initial_info(user)

    pending_entries = []

    if hasattr(user, 'appentry_set'):
        pending_entries = user.appentry_set.filter(
            is_approved__isnull=True  # pending
        )

        # if an application entry was submitted
        # after your current membership was created
        user_membership = user.memberships.get_membership()
        if user_membership:
            pending_entries.filter(
                entry_time__gte=user_membership.subscribe_dt
            )

    try:
        app_entry_form = AppEntryForm(
                app,
                request.POST or None,
                request.FILES or None,
                user=user,
                corporate_membership=corporate_membership,
                initial=initial_dict
            )
    except NoMembershipTypes as e:
        print e

        user_memberships = None
        if hasattr(user, 'memberships'):
            user_memberships = user.memberships.all()
        # non-admin has no membership-types available in this application
        # let them know to wait for their renewal period before trying again
        return render_to_response("memberships/applications/no-renew.html", {
            "app": app, "user": user, "memberships": user_memberships},
            context_instance=RequestContext(request))

    if request.method == "POST":
        if app_entry_form.is_valid():

            entry = app_entry_form.save(commit=False)
            entry_invoice = entry.save_invoice()

            if user.is_authenticated():
                entry.user = user
                entry.is_renewal = all(is_only_a_member)

            # add all permissions and save the model
            entry = update_perms_and_save(request, app_entry_form, entry)

            # administrators go to approve/disapprove page
            if user.profile.is_superuser:
                return redirect(reverse('membership.application_entries', args=[entry.pk]))

            # send "joined" notification
            Notice.send_notice(
                entry=entry,
                request=request,
                emails=entry.email,
                notice_type='join',
                membership_type=entry.membership_type,
            )

            if entry_invoice.total == 0:
                if not entry_invoice.is_tendered:
                    entry_invoice.tender(request.user)

            # online payment
            if entry_invoice.total > 0 and entry.payment_method and entry.payment_method.is_online:

                return HttpResponseRedirect(reverse(
                    'payment.pay_online',
                    args=[entry_invoice.pk, entry_invoice.guid]
                ))

            if not entry.approval_required():

                entry.user, created = entry.get_or_create_user()
                if created:
                    send_welcome_email(entry.user)

                entry.approve()

                # silence old memberships within renewal period
                Membership.objects.silence_old_memberships(entry.user)

                # get user from the membership since it's null in the entry
                entry.user = entry.membership.user

                # send "approved" notification
                Notice.send_notice(
                    request=request,
                    emails=entry.email,
                    notice_type='approve',
                    membership=entry.membership,
                    membership_type=entry.membership_type,
                )

                # log - entry approval
                EventLog.objects.log(instance=entry)

            # log - entry submission
            EventLog.objects.log(instance=entry)

            return redirect(entry.confirmation_url)

    return render_to_response(template_name, {
            'app': app,
            'app_entry_form': app_entry_form,
            'pending_entries': pending_entries,
            }, context_instance=RequestContext(request))


def application_details_corp_pre(request, slug, cmb_id=None, template_name="memberships/applications/details_corp_pre.html"):
    # redirect to the new system
    return redirect(reverse('membership_default.corp_pre_add'))

    try:
        app = App.objects.get(slug=slug)
    except App.DoesNotExist:
        raise Http404

    if not hasattr(app, 'corp_app'):
        raise Http404

    if not app.corp_app:
        raise Http404

    form = AppCorpPreForm(request.POST or None)
    if request.user.profile.is_superuser or app.corp_app.authentication_method == 'admin':
        del form.fields['secret_code']
        del form.fields['email']
        from utils import get_corporate_membership_choices
        form.fields['corporate_membership_id'].choices = get_corporate_membership_choices()
        if cmb_id:
            form.fields['corporate_membership_id'].initial = cmb_id
        form.auth_method = 'corporate_membership_id'

    elif app.corp_app.authentication_method == 'email':
        del form.fields['corporate_membership_id']
        del form.fields['secret_code']
        form.auth_method = 'email'
    else:  # secret_code
        del form.fields['corporate_membership_id']
        del form.fields['email']
        form.auth_method = 'secret_code'

    if request.method == "POST":
        if form.is_valid():
            # find the corporate_membership_id and redirect to membership.application_details
            if form.auth_method == 'corporate_membership_id':
                corporate_membership_id = form.cleaned_data['corporate_membership_id']
            else:
                corporate_membership_id = form.corporate_membership_id

                if form.auth_method == 'email':
                    corp_memb = CorporateMembership.objects.get(pk=corporate_membership_id)
                    try:
                        indiv_veri = IndivMembEmailVeri8n.objects.get(corporate_membership=corp_memb,
                                                                verified_email=form.cleaned_data['email'])
                        if indiv_veri.verified:
                            is_verified = True
                        else:
                            is_verified = False
                    except IndivMembEmailVeri8n.DoesNotExist:
                        is_verified = False
                        indiv_veri = IndivMembEmailVeri8n()
                        indiv_veri.corporate_membership = corp_memb
                        indiv_veri.verified_email = form.cleaned_data['email']
                        if request.user and not request.user.is_anonymous():
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
                        send_email_notification('membership_corp_indiv_verify_email', recipients, extra_context)

                        return redirect(reverse('membership.email__to_verify_conf'))
                    else:
                        # the email address is verified
                        return redirect(reverse('membership.application_details_via_corp_domain',
                                                args=[app.slug,
                                                indiv_veri.corporate_membership.id,
                                                indiv_veri.pk,
                                                indiv_veri.guid]))
                if form.auth_method == 'secret_code':
                    # secret code hash
                    random_string = User.objects.make_random_password(length=4, allowed_chars='abcdefghjkmnpqrstuvwxyz')
                    request.session['corp_hash_random_string'] = random_string
                    secret_code = form.cleaned_data['secret_code']
                    secret_hash = md5('%s%s' % (secret_code, random_string)).hexdigest()
                    return redirect(reverse('membership.application_details_via_corp_secret_code',
                                            args=[app.slug,
                                                corporate_membership_id,
                                                secret_hash]))

            return redirect(reverse('membership.application_details_default', args=[app.slug, corporate_membership_id]))

    c = {'app': app, "form": form}
    return render_to_response(template_name, c,
        context_instance=RequestContext(request))


def application_confirmation_default(request, hash):
    """
    Responds with default confirmation
    """
    from django.contrib.auth import login

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

    return render_to_response(
        template_name, {
        'is_confirmation': True,
        'membership': membership,
        'app': app
        }, context_instance=RequestContext(request))


def application_confirmation(request, hash=None, template_name="memberships/entries/details.html"):
    """
    Display this confirmation have a membership application is submitted.
    """

    if not hash:
        raise Http404

    entry = get_object_or_404(AppEntry, hash=hash)

    return render_to_response(template_name, {'is_confirmation': True, 'entry': entry},
        context_instance=RequestContext(request))


@login_required
def application_entries(request, id=None, template_name="memberships/entries/details.html"):
    """
    Displays the details of a membership application entry.
    """

    if not id:
        return redirect(reverse('membership.application_entries_search'))

    entry = get_object_or_404(AppEntry, id=id)
    if not entry.allow_view_by(request.user):
        raise Http403

    EventLog.objects.log(instance=entry)

    approve_perm = has_perm(request.user, "memberships.approve_membership")

    if request.method == "POST":
        # perm required for approval
        if not approve_perm:
            raise Http403

        form = MemberApproveForm(entry, request.POST)
        if form.is_valid():

            status = request.POST.get('status', '')
            approve = (status.lower() == 'approve') or (status.lower() == 'approve renewal')

            entry.judge = request.user

            if approve:
                user_pk = int(form.cleaned_data['users'])
                if user_pk:
                    entry.user = User.objects.get(pk=user_pk)
                else:
                    entry.user = User.objects.create_user(**{
                        'username': entry.spawn_username(entry.first_name, entry.last_name),
                        'email': entry.email,
                        'password': hashlib.sha1(entry.email).hexdigest()[:6]
                    })
                    send_welcome_email(entry.user)

                # update application, user,
                # group, membership, and archive
                entry.approve()

                # silence old memberships within renewal period
                Membership.objects.silence_old_memberships(entry.user)

                # execute field functions (group subscriptions)
                entry.execute_field_functions()

                # send "approved" notification
                Notice.send_notice(
                    request=request,
                    entry=entry,
                    emails=entry.email,
                    notice_type='approve',
                    membership=entry.membership,
                    membership_type=entry.membership_type,
                )

                EventLog.objects.log(instance=entry, action="approve")

            else:  # if not approved
                entry.disapprove()

                # send "disapproved" notification
                Notice.send_notice(
                    entry=entry,
                    request=request,
                    emails=entry.email,
                    notice_type='disapprove',
                    membership_type=entry.membership_type,
                )

                EventLog.objects.log(instance=entry, action="disapprove")

            return redirect(reverse('membership.application_entries', args=[entry.pk]))

    else:  # if request != POST
        form = MemberApproveForm(entry)

    return render_to_response(template_name, {
        'entry': entry,
        'form': form,
        'can_approve': approve_perm,
        }, context_instance=RequestContext(request))


@login_required
def application_entries_print(request, id=None, template_name="memberships/entries/print-details.html"):
    """
    Displays the print details of a membership application entry.
    """

    if not id:
        return redirect(reverse('membership.application_entries_search'))

    entry = get_object_or_404(AppEntry, id=id)
    if not entry.allow_view_by(request.user):
        raise Http403

    # log entry view
    EventLog.objects.log(**{
        'event_id': 1085001,
        'event_data': '%s (%d) print viewed by %s' % (entry._meta.object_name, entry.pk, request.user),
        'description': '%s print viewed' % entry._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': entry,
    })

    return render_to_response(template_name, {
        'entry': entry,
        }, context_instance=RequestContext(request))


@login_required
def entry_edit(request, id=0, template_name="memberships/entries/edit.html"):
    """
    Edit membership application entry page.
    """
    entry = get_object_or_404(AppEntry, id=id)  # exists

    if not request.user.profile.is_superuser:
        raise Http403  # not permitted

    if request.method == "POST":
        form = EntryEditForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save()

            EventLog.objects.log(instance=entry)

            messages.add_message(
                request,
                messages.INFO,
                'Entry Sucessfully Updated',
            )

            return redirect(reverse('membership.application_entries', args=[entry.pk]))

    else:
        form = EntryEditForm(instance=entry)

    return render_to_response(template_name, {
        'entry': entry,
        'form': form,
        }, context_instance=RequestContext(request))


@login_required
def entry_delete(request, id=0, template_name="memberships/entries/delete.html"):
    """
    Delete membership application entry.
    """
    entry = get_object_or_404(AppEntry, id=id)  # exists

    if not request.user.profile.is_superuser:
        raise Http403  # not permitted

    if request.method == "POST":
        EventLog.objects.log(instance=entry)
        messages.add_message(request, messages.INFO, "Deleted %s" % entry)
        entry.delete()

        return redirect("membership.application_entries_search")

    return render_to_response(template_name, {
        'entry': entry,
    }, context_instance=RequestContext(request))


@login_required
def application_entries_search(request, template_name="memberships/entries/search.html"):
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

    return render_to_response(template_name, {
        'notice': notice,
        }, context_instance=RequestContext(request))


@login_required
@password_required
def membership_import_upload(request, template_name='memberships/import-upload-file.html'):
    """
    This is the upload view for the membership imports.
    This will upload the membership import file and then redirect the user
    to the import mapping/preview page of the import file
    """

    if not request.user.profile.is_superuser:
        raise Http403

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            # reset the password_promt session
            del request.session['password_promt']
            cleaned_data = form.cleaned_data
            app = cleaned_data['app']
            interactive = cleaned_data['interactive']
            override = cleaned_data['override']
            key = cleaned_data['key']

            memport = MembershipImport.objects.create(
                app=app,
                interactive=interactive,
                override=override,
                key=key,
                creator=request.user
            )

            csv = File.objects.save_files_for_instance(request, memport)[0]

            # hiding membership import
            csv.allow_anonymous_view = False
            csv.allow_user_view = False
            csv.is_public = False
            csv.save()

            file_path = unicode(csv.file.name)

            import_valid, import_errs = is_import_valid(file_path)

            EventLog.objects.log()

            if not import_valid:
                for err in import_errs:
                    messages.add_message(request, messages.ERROR, err)
                memport.delete()
                return redirect('membership_import_upload_file')

            return redirect('membership_import_preview', memport.id)
    else:
        form = UploadForm()

    return render_to_response(template_name, {
        'form': form,
        'datetime': datetime,
        }, context_instance=RequestContext(request))


@login_required
def membership_import_preview(request, id):
    """
    This will generate a form based on the uploaded CSV for field mapping.
    A preview will be generated based on the mapping given.
    """
    if not request.user.profile.is_superuser:
        raise Http403

    memport = get_object_or_404(MembershipImport, pk=id)

    if request.method == 'POST':
        form = ImportMapForm(request.POST, memport=memport)

        if form.is_valid():
            #show the user a preview based on the mapping
            cleaned_data = form.cleaned_data
            file_path = memport.get_file().file.name
            memberships, stats = parse_mems_from_csv(
                file_path,
                cleaned_data,
                membership_import=memport
            )

            EventLog.objects.log()

            # return the form to use it for the confirm view
            template_name = 'memberships/import-preview.html'
            return render_to_response(template_name, {
                'memberships': memberships,
                'stats': stats,
                'memport': memport,
                'form': form,
                'datetime': datetime,
            }, context_instance=RequestContext(request))

    else:
        form = ImportMapForm(memport=memport)

    template_name = 'memberships/import-map-fields.html'
    return render_to_response(template_name, {
        'form': form,
        'memport': memport,
        'datetime': datetime,
        }, context_instance=RequestContext(request))


@login_required
def membership_import_confirm(request, id):
    """
    Confirm the membership import and continue with the process.
    This can only be accessed via a hidden post form from the preview page.
    That will hold the original mappings selected by the user.
    """
    if not request.user.profile.is_superuser:
        raise Http403

    memport = get_object_or_404(MembershipImport, pk=id)

    if request.method == "POST":
        form = ImportMapForm(request.POST, memport=memport)

        if form.is_valid():
            cleaned_data = form.cleaned_data

            EventLog.objects.log()

            if not settings.CELERY_IS_ACTIVE:
                result = ImportMembershipsTask()
                memberships, stats = result.run(memport, cleaned_data)
                return render_to_response('memberships/import-confirm.html', {
                    'memberships': memberships,
                    'stats': stats,
                    'datetime': datetime,
                }, context_instance=RequestContext(request))
            else:
                result = ImportMembershipsTask.delay(memport, cleaned_data)

            # updates membership protection
            # uses setting on membership settings page
            call_command('membership_update_protection')

            return redirect('membership_import_status', result.task_id)
    else:
        return redirect('membership_import_preview', memport.id)


@login_required
def membership_import_status(request, task_id, template_name='memberships/import-confirm.html'):
    """
    Checks if a membership import is completed.
    """
    if not request.user.profile.is_superuser:
        raise Http403

    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        #tasks database entries are not created at once.
        task = None

    if task and task.status == "SUCCESS":

        memberships, stats = task.result

        return render_to_response(template_name, {
            'memberships': memberships,
            'stats': stats,
            'datetime': datetime,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('memberships/import-status.html', {
            'task': task,
            'datetime': datetime,
        }, context_instance=RequestContext(request))


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
    user_fks = [field.name for field in User._meta.fields \
                if isinstance(field, (ForeignKey, OneToOneField))]
    profile_fks = [field.name for field in Profile._meta.fields \
                   if isinstance(field, (ForeignKey, OneToOneField))]
    memb_fks = [field.name for field in MembershipDefault._meta.fields \
                if isinstance(field, (ForeignKey, OneToOneField))]

    fks = Set(user_fks + profile_fks + memb_fks)
    fks = [field for field in fks]
    if 'user' in fks:
        fks.remove('user')
    fks.sort()
    foreign_keys = ', '.join(fks)

    return render_to_response(template_name, {
        'form': form,
        'memb_type_exists': memb_type_exists,
        'memb_app_exists': memb_app_exists,
        'foreign_keys': foreign_keys
        }, context_instance=RequestContext(request))


@login_required
def membership_default_import_preview(request, mimport_id,
                template_name='memberships/import_default/preview.html'):
    """
    Preview the import
    """

    if not request.user.profile.is_superuser:
        raise Http403

    invalidate('memberships_membershipimport')
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
                fieldnames = idata.row_data.keys()

        return render_to_response(template_name, {
            'mimport': mimport,
            'users_list': users_list,
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
                return redirect(reverse('memberships.default_import_status',
                                     args=[mimport.id]))
        else:
            if mimport.status == 'not_started':
                subprocess.Popen(["python", "manage.py",
                              "membership_import_preprocess",
                              str(mimport.pk)])

            return render_to_response(template_name, {
                'mimport': mimport,
                }, context_instance=RequestContext(request))


@login_required
def membership_default_import_process(request, mimport_id):
    """
    Process the import
    """
    if not request.user.profile.is_superuser:
        raise Http403
    invalidate('memberships_membershipimport')
    mimport = get_object_or_404(MembershipImport,
                                    pk=mimport_id)
    if mimport.status == 'preprocess_done':
        mimport.status = 'processing'
        mimport.num_processed = 0
        mimport.save()
        # start the process
        subprocess.Popen(["python", "manage.py",
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
    invalidate('memberships_membershipimport')
    mimport = get_object_or_404(MembershipImport,
                                    pk=mimport_id)
    if mimport.status not in ('processing', 'completed'):
        return redirect(reverse('memberships.default_import'))

    return render_to_response(template_name, {
        'mimport': mimport,
        }, context_instance=RequestContext(request))


@login_required
def membership_default_import_download_recap(request, mimport_id):
    """
    Download import recap.
    """

    if not request.user.profile.is_superuser:
        raise Http403
    invalidate('memberships_membershipimport')
    mimport = get_object_or_404(MembershipImport,
                                    pk=mimport_id)
    mimport.generate_recap()
    filename = os.path.split(mimport.recap_file.name)[1]

    recap_path = mimport.recap_file.name
    if default_storage.exists(recap_path):
        response = HttpResponse(default_storage.open(recap_path).read(),
                                mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
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
    invalidate('memberships_membershipimport')
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
    invalidate('memberships_membershipimport')
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

    title_list = [field for field in MembershipDefault._meta.fields \
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
                  'url', 'url2', 'address_type', 'fax',
                  'work_phone', 'home_phone', 'mobile_phone',
                  'dob', 'ssn', 'spouse',
                  'department', 'ud1', 'ud2', 'ud3', 'ud4', 'ud5',
                  'ud6', 'ud7', 'ud8', 'ud9', 'ud10',
                  'ud11', 'ud12', 'ud13', 'ud14', 'ud15',
                  'ud16', 'ud17', 'ud18', 'ud19', 'ud20',
                  'ud21', 'ud22', 'ud23', 'ud24', 'ud25',
                  'ud26', 'ud27', 'ud28', 'ud29', 'ud30',
                  ] + title_list
    data_row_list = []

    return render_csv(filename, title_list,
                        data_row_list)


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
            temp_file_path = 'export/memberships/%s_%d_temp.csv' % (identifier, cp_id)
            default_storage.save(temp_file_path, ContentFile(''))

            # start the process
            subprocess.Popen(["python", "manage.py",
                          "membership_export_process",
                          '--export_fields=%s' % export_fields,
                          '--export_type=%s' % export_type,
                          '--export_status_detail=%s' % export_status_detail,
                          '--identifier=%s' % identifier,
                          '--user=%s' % request.user.id,
                          '--cp_id=%d' % cp_id])
            # log an event
            EventLog.objects.log()
            status_url = reverse('memberships.default_export_status', args=[identifier])

            if cp_id:
                status_url = '%s?cp_id=%d' % (status_url, cp_id)

            return redirect(status_url)

    context = {"form": form,
               'corp_profile': corp_profile}
    return render_to_response(template, context, RequestContext(request))


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
    return render_to_response(template, context, RequestContext(request))


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

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=membership_export_%s' % file_name
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
        render_to_string('memberships/app_fields.json'))
    return HttpResponse(simplejson.dumps(complete_list))


@csrf_exempt
@login_required
def get_taken_fields(request):
    """
    Returns a list of json fields no longer available.
    Data type returned is JSON.
    """
    app_pk = request.POST.get('app_pk') or 0
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
    demographics_form = DemographicsForm(app_fields)
    membership_form = MembershipDefault2Form(app_fields,
                                             request_user=request.user,
                                             membership_app=app)
    #print membership_form.field_names

    context = {'app': app,
               "app_fields": app_fields,
               'user_form': user_form,
               'profile_form': profile_form,
               'demographics_form': demographics_form,
               'membership_form': membership_form}
    return render_to_response(template, context, RequestContext(request))


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

    return redirect(reverse('membership_default.add', args=[app.slug]))


def membership_default_add(request, slug='', template='memberships/applications/add.html', **kwargs):
    """
    Default membership application form.
    """
    from tendenci.addons.memberships.models import Notice

    user = None
    membership = None
    username = request.GET.get('username', u'')

    if not request.user.is_superuser:
        if request.user.is_authenticated():
            username = username or request.user.username

    membership_type_id = request.GET.get('membership_type_id', u'')
    if membership_type_id.isdigit():
        membership_type_id = int(membership_type_id)
    else:
        membership_type_id = 0

    allowed_users = (
        request.user.profile.is_superuser,
        username == request.user.username,
    )

    if any(allowed_users) and username:
        [user] = User.objects.filter(username=username)[:1] or [None]

    join_under_corporate = kwargs.get('join_under_corporate', False)
    corp_membership = None

    if join_under_corporate:
        corp_app = CorpMembershipApp.objects.current_app()
        if not corp_app:
            raise Http404

        app = corp_app.memb_app

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

        # imv = individual membership verification
        imv_id = kwargs.get('imv_id', 0)
        imv_guid = kwargs.get('imv_guid')

        secret_hash = kwargs.get('secret_hash', '')

        is_verified = False
        authentication_method = corp_app.authentication_method

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
            tmp_secret_hash = md5('%s%s' % (corp_membership.corp_profile.secret_code,
                        request.session.get('corp_hash_random_string', ''))
                                  ).hexdigest()
            if secret_hash == tmp_secret_hash:
                is_verified = True

        if not is_verified:
            return redirect(reverse('membership_default.corp_pre_add',
                                    args=[cm_id]))

    else:  # regular membership

        app = get_object_or_404(MembershipApp, slug=slug)

        if app.use_for_corp:
            redirect_url = reverse('membership_default.corp_pre_add')

            if username:
                return HttpResponseRedirect(
                    '%s?username=%s' % (redirect_url, username))
            return redirect(redirect_url)

    if not app:
        raise Http404

    if join_under_corporate:
        app_fields = app.fields.filter(Q(display=True) | Q(
            field_name='corporate_membership_id'))
    else:
        app_fields = app.fields.filter(display=True)

    if not request.user.profile.is_superuser:
        app_fields = app_fields.filter(admin_only=False)

    app_fields = app_fields.order_by('position')
    if not join_under_corporate:
        # exclude the corp memb field if not join under corporate
        app_fields = app_fields.exclude(field_name='corporate_membership_id')

    user_initial = {}
    if user:
        user_initial = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }

    user_form = UserForm(
        app_fields,
        request.POST or None,
        request=request,
        initial=user_initial)

    profile_form = ProfileForm(app_fields, request.POST or None)

    profile_initial = {}
    if user:
        profile_initial = {
            'salutation': user.profile.salutation,
            'phone': user.profile.phone,
            'phone2': user.profile.phone2,
            'address': user.profile.address,
            'address2': user.profile.address2,
            'city': user.profile.city,
            'state': user.profile.state,
            'zipcode': user.profile.zipcode,
            'county': user.profile.county,
            'country': user.profile.country,
            'address_type': user.profile.address_type,
            'url': user.profile.url,
            'display_name': user.profile.display_name,
            'mailing_name': user.profile.mailing_name,
            'company': user.profile.company,
            'position_title': user.profile.position_title,
            'position_assignment': user.profile.position_assignment,
            'fax': user.profile.fax,
            'work_phone': user.profile.work_phone,
            'home_phone': user.profile.home_phone,
            'mobile_phone': user.profile.mobile_phone,
            'email2': user.profile.email2,
            'dob': user.profile.dob,
            'spouse': user.profile.spouse,
            'department': user.profile.department,
        }

    profile_form = ProfileForm(
        app_fields,
        request.POST or None,
        initial=profile_initial
    )

    params = {
        'request_user': request.user,
        'customer': user or request.user,
        'membership_app': app,
        'join_under_corporate': join_under_corporate,
        'corp_membership': corp_membership,
    }

    if join_under_corporate:
        params['authentication_method'] = authentication_method

    demographics_form = DemographicsForm(app_fields, request.POST or None)

    if user:
        [membership] = user.membershipdefault_set.filter(
            membership_type=membership_type_id).order_by('-pk')[:1] or [None]

    membership_initial = {}
    if membership:
        membership_initial = {
            'membership_type': membership.membership_type,
            'payment_method': membership.payment_method,
            'certifications': membership.certifications,
            'work_experience': membership.work_experience,
            'referral_source': membership.referral_source,
            'referral_source_other': membership.referral_source_other,
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
        }
    multiple_membership = app.allow_multiple_membership
    if membership or join_under_corporate:
        multiple_membership = False

    membership_form = MembershipDefault2Form(app_fields,
        request.POST or None, initial=membership_initial,
        multiple_membership=multiple_membership, **params)

    captcha_form = CaptchaForm(request.POST or None)
    if request.user.is_authenticated() or not app.use_captcha:
        del captcha_form.fields['captcha']

    if (not app.discount_eligible or 
        not Discount.has_valid_discount(model=MembershipSet._meta.module_name)):
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
            invoice = membership_set.save_invoice(memberships)

            discount_code = membership_form2.cleaned_data.get('discount_code', None)
            discount_amount = Decimal(0)
            discount_list = [Decimal(0) for i in range(len(amount_list))]
            if discount_code:
                [discount] = Discount.objects.filter(
                    discount_code=discount_code, apps__model=MembershipSet._meta.module_name)[:1] or [None]
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

            memberships_join_notified = []
            memberships_renewal_notified = []
            for membership in memberships:
                membership.membership_set = membership_set

                approval_required = (
                    membership.approval_required(),
                    join_under_corporate and authentication_method == 'admin')

                if any(approval_required):
                    membership.pend()
                    membership.save()  # save pending status

                    if membership.is_renewal():
                        Notice.send_notice(
                            request=request,
                            emails=membership.user.email,
                            notice_type='renewal',
                            membership=membership,
                            membership_type=membership.membership_type,
                        )
                        memberships_renewal_notified.append(membership)

                    else:
                        Notice.send_notice(
                            request=request,
                            emails=membership.user.email,
                            notice_type='join',
                            membership=membership,
                            membership_type=membership.membership_type,
                        )
                        memberships_join_notified.append(membership)
                else:
                    membership.approve(request_user=customer)
                    membership.send_email(request, 'approve')

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
        'demographics_form': demographics_form,
        'membership_form': membership_form,
        'captcha_form': captcha_form
    }
    return render_to_response(template, context, RequestContext(request))


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

        from utils import get_corporate_membership_choices
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
                        if request.user and not request.user.is_anonymous():
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
                    secret_hash = md5('%s%s' % (secret_code, random_string)).hexdigest()
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

    return render_to_response(template_name, c,
        context_instance=RequestContext(request))


def email_to_verify_conf(request,
        template_name="memberships/applications/email_to_verify_conf.html"):
    return render_to_response(template_name,
        context_instance=RequestContext(request))


def verify_email(request,
                 id=0,
                 guid=None,
                 template_name="memberships/applications/verify_email.html"):
    indiv_veri = get_object_or_404(IndivEmailVerification, id=id, guid=guid)
    if not indiv_veri.verified:
        indiv_veri.verified = True
        indiv_veri.verified_dt = datetime.now()
        if request.user and not request.user.is_anonymous():
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


@staff_member_required
def membership_join_report(request):
    TODAY = date.today()
    memberships = MembershipDefault.objects.all()
    membership_type = u''
    membership_status = u''
    start_date = u''
    end_date = u''

    start_date = TODAY - timedelta(days=30)
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

    memberships = memberships.filter(
        join_dt__gte=start_date, join_dt__lte=end_date).order_by('join_dt')

    EventLog.objects.log()

    return render_to_response(
        'reports/membership_joins.html', {
        'membership_type': membership_type,
        'membership_status': membership_status,
        'start_date': start_date,
        'end_date': end_date,
        'memberships': memberships,
        'form': form,
        }, context_instance=RequestContext(request))


@staff_member_required
@password_required
def membership_export(request):
    template_name = 'memberships/export.html'
    form = ExportForm(request.POST or None, user=request.user)

    if request.method == 'POST':
        if form.is_valid():
            # reset the password_promt session
            del request.session['password_promt']
            app = form.cleaned_data['app']
            export_id = run_export_task('memberships', 'membership', [], app)
            return redirect('export.status', export_id)

    return render_to_response(template_name, {
            'form': form
            }, context_instance=RequestContext(request))


@staff_member_required
def membership_join_report_pdf(request):
    TODAY = date.today()
    mem_type = request.GET.get('mem_type', u'')
    mem_stat = request.GET.get('mem_stat', u'')
    start_date = request.GET.get('start_date', u'')
    end_date = request.GET.get('end_date', u'')

    mems = MembershipDefault.objects.all()

    if mem_type:
        mems = mems.filter(membership_type=mem_type)

    if mem_stat:
        mems = mems.filter(status_detail=mem_stat.lower())

    if start_date:
        start_date = parse(start_date)  # make date object
    else:
        start_date = TODAY - timedelta(days=30)

    if end_date:
        end_date = parse(end_date)  # make date object
    else:
        end_date = TODAY

    mems = mems.filter(
        join_dt__gte=start_date, join_dt__lte=end_date).order_by('join_dt')

    if not mems:
        raise Http404

    report = ReportNewMems(queryset=mems)
    response = HttpResponse(mimetype='application/pdf')
    report.generate_by(PDFGenerator, filename=response)

    EventLog.objects.log()

    return response


@staff_member_required
def report_list(request, template_name='reports/membership_report_list.html'):
    """ List of all available membership reports.
    """

    EventLog.objects.log()

    return render_to_response(template_name, context_instance=RequestContext(request))


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

    return render_to_response(template_name, {
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
            }, context_instance=RequestContext(request))


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
        mems = mems.order_by('subscribe_dt')
        is_ascending_subscription = False
    elif sort == '-subscription':
        mems = mems.order_by('-subscribe_dt')
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

    return render_to_response(template_name, {
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
            }, context_instance=RequestContext(request))


@staff_member_required
def report_members_summary(request, template_name='reports/membership_summary.html'):
    days = get_days(request)

    chart_data = prepare_chart_data(days)

    EventLog.objects.log()

    return render_to_response(template_name, {
                'chart_data': chart_data,
                'date_range': (days[0], days[-1]),
            }, context_instance=RequestContext(request))


@staff_member_required
def report_members_over_time(request, template_name='reports/membership_over_time.html'):
    stats = get_over_time_stats()

    EventLog.objects.log()

    return render_to_response(template_name, {
        'stats': stats,
    }, context_instance=RequestContext(request))


@staff_member_required
def report_members_stats(request, template_name='reports/membership_stats.html'):
    """Shows a report of memberships per membership type.
    """
    summary, total = get_membership_stats()

    EventLog.objects.log()

    return render_to_response(template_name, {
        'summary': summary,
        'total': total,
        }, context_instance=RequestContext(request))


@staff_member_required
def report_member_roster(request, template_name='reports/membership_roster.html'):
    """ Shows membership roster. Extends base-print for easy printing.
    """
    members = MembershipDefault.objects.filter(status=1, status_detail="active").order_by('user__last_name')

    EventLog.objects.log()

    return render_to_response(template_name, {'members': members}, context_instance=RequestContext(request))


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

            table_data.append([
                mem.user.first_name,
                mem.user.last_name,
                mem.user.profile.company
            ])

        return render_csv(
            'current-members-quicklist.csv',
            table_header,
            table_data,
        )
    # ------------------------------------

    EventLog.objects.log()

    return render_to_response(template_name, {'members': members}, context_instance=RequestContext(request))


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

    return render_to_response(template_name, {'companies': companies}, context_instance=RequestContext(request))


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

    return render_to_response(template_name, {'members': members, 'days': days}, context_instance=RequestContext(request))


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

    return render_to_response(template_name, {'members': members}, context_instance=RequestContext(request))


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

    return render_to_response(template_name, {'members': members}, context_instance=RequestContext(request))


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
    return render_to_response(template_name,
                              {'months': months,
                               'total_new': total_new,
                               'total_renew': total_renew,
                               'years': years,
                               'year_selected': year_selected,
                               'exclude_total': exclude_total},
                              context_instance=RequestContext(request))


@staff_member_required
def report_members_ytd_type(request, template_name='reports/members_ytd_type.html'):
    import datetime

    year = datetime.datetime.now().year
    years = [year, year - 1, year - 2, year - 3, year - 4]
    if request.GET.get('year'):
        year = int(request.GET.get('year'))

    types_new = []
    types_renew = []
    types_expired = []
    months = calendar.month_abbr[1:]
    itermonths = iter(calendar.month_abbr)
    next(itermonths)

    for type in MembershipType.objects.all():
        mems = MembershipDefault.objects.filter(membership_type=type)
        for index, month in enumerate(itermonths):
            index = index + 1
            new_mems = mems.filter(join_dt__year=year, join_dt__month=index).count()
            renew_mems = mems.filter(renew_dt__year=year, renew_dt__month=index).count()
            expired_mems = mems.filter(expire_dt__year=year, expire_dt__month=index).count()
            new_dict = {
                'name': type.name,
                'new_mems': new_mems,
            }
            types_new.append(new_dict)
            renew_dict = {
                'name': type.name,
                'renew_mems': renew_mems,
            }
            types_renew.append(renew_dict)
            expired_dict = {
                'name': type.name,
                'expired_mems': expired_mems,
            }
            types_expired.append(expired_dict)

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

    return render_to_response(template_name, {'months': months, 'years': years, 'year': year, 'types_new': types_new, 'types_renew': types_renew, 'types_expired': types_expired, 'totals_new': totals_new, 'totals_renew': totals_renew, 'totals_expired': totals_expired}, context_instance=RequestContext(request))
