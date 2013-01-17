import os
import math
from datetime import datetime, date, time
import csv
import operator
from hashlib import md5
from sets import Set
import subprocess

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
from johnny.cache import invalidate

from tendenci.core.imports.utils import render_excel
from tendenci.core.exports.utils import render_csv

from tendenci.core.base.http import Http403
from tendenci.core.perms.utils import has_perm
from tendenci.core.base.decorators import password_required
from tendenci.core.event_logs.models import EventLog

from tendenci.addons.corporate_memberships.models import (
                                            CorpMembershipApp,
                                            CorpMembershipRep,
                                            CorpMembership,
                                            CorpProfile,
                                            IndivMembershipRenewEntry,
                                            CorpMembershipAppField,
                                            CorpMembershipImport,
                                            CorpMembershipImportData,
                                            CorpApp, CorpField,
                                            CorporateMembership,
                                          CorporateMembershipType,
                                          CorporateMembershipRep, 
                                          Creator,
                                          CorpMembRenewEntry, 
                                          IndivMembRenewEntry,
                                          CorpFieldEntry,
                                          AuthorizedDomain)
from tendenci.addons.corporate_memberships.forms import (
                                         CorpMembershipForm,
                                         CorpProfileForm,
                                         CorpMembershipRenewForm,
                                         RosterSearchAdvancedForm,
                                         CorpMembershipSearchForm,
                                         CorpMembershipUploadForm,
                                         CorpExportForm,
                                         CorpMembershipRepForm,
                                         CorpMembForm, 
                                         CreatorForm,
                                         CorpApproveForm,
                                         CorpMembRepForm, 
                                         RosterSearchForm, 
                                         CorpMembRenewForm,
                                         CSVForm,
                                         ExportForm)
from tendenci.addons.corporate_memberships.utils import (
                                        get_corporate_membership_type_choices,
                                         get_payment_method_choices,
                                         get_indiv_memberships_choices,
                                         corp_membership_rows,
                                         corp_membership_update_perms,
                                         get_corp_memb_summary,
                                         corp_memb_inv_add, 
                                         dues_rep_emails_list,
                                         corp_memb_update_perms,
                                         validate_import_file,
                                         new_corp_mems_from_csv,
                                         get_over_time_stats,
                                         get_indiv_membs_choices,
                                         get_summary)
from tendenci.addons.corporate_memberships.import_processor import CorpMembershipImportProcessor
#from tendenci.addons.memberships.models import MembershipType
from tendenci.addons.memberships.models import (Membership,
                                                MembershipDefault)

from tendenci.core.perms.utils import get_notice_recipients
from tendenci.core.base.utils import send_email_notification
from tendenci.core.files.models import File
from tendenci.apps.profiles.models import Profile
from tendenci.addons.corporate_memberships.settings import use_search_index
from tendenci.core.site_settings.utils import get_setting


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


@login_required
def app_preview(request, app_id,
                    template='corporate_memberships/applications/preview.html'):
    """
    Corporate membership application preview.
    """
    app = get_object_or_404(CorpMembershipApp, pk=app_id)
    is_superuser = request.user.profile.is_superuser
    app_fields = app.fields.filter(display=True)
    if not is_superuser:
        app_fields = app_fields.filter(admin_only=False)
    app_fields = app_fields.order_by('order')

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
            return HttpResponseRedirect('%s%s' % (reverse('corpmembership.add'),
                                              '?hash=%s' % hash))

    context = {"form": form,
               'corp_app': app}
    return render_to_response(template, context, RequestContext(request))


def corpmembership_add(request,
                       template='corporate_memberships/applications/add.html'):
    """
    Corporate membership add.
    """
    app = CorpMembershipApp.objects.current_app()
    if not app:
        raise Http404
    is_superuser = request.user.profile.is_superuser
    creator = None
    hash = request.GET.get('hash', '')
    if not request.user.is_authenticated():
        if hash:
            [creator] = Creator.objects.filter(hash=hash)[:1] or [None]
        if not creator:
            # anonymous user - redirect them to enter their
            # contact email before processing
            return HttpResponseRedirect(reverse('corpmembership.add_pre'))

    app_fields = app.fields.filter(display=True)
    if not is_superuser:
        app_fields = app_fields.filter(admin_only=False)
    app_fields = app_fields.order_by('order')

    corpprofile_form = CorpProfileForm(app_fields,
                                     request.POST or None,
                                     request_user=request.user,
                                     corpmembership_app=app)
    corpmembership_form = CorpMembershipForm(app_fields,
                                             request.POST or None,
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
            # calculate the expiration
            corp_memb_type = corp_membership.corporate_membership_type
            corp_membership.expiration_dt = corp_memb_type.get_expiration_dt(
                                        join_dt=corp_membership.join_dt)

            # add invoice
            inv = corp_memb_inv_add(request.user, corp_membership)
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

            return HttpResponseRedirect(reverse('corpmembership.add_conf',
                                                args=[corp_membership.id]))

    context = {'app': app,
               "app_fields": app_fields,
               'corpprofile_form': corpprofile_form,
               'corpmembership_form': corpmembership_form}
    return render_to_response(template, context, RequestContext(request))


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
    app_fields = app_fields.order_by('order')

    corpprofile_form = CorpProfileForm(app_fields,
                                     request.POST or None,
                                     instance=corp_profile,
                                     request_user=request.user,
                                     corpmembership_app=app)
    corpmembership_form = CorpMembershipForm(app_fields,
                                             request.POST or None,
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

    app_fields = list(app_fields.order_by('order'))

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
    context = {"corporate_membership": corp_membership,
               'app_fields': app_fields,
               'app': app}
    return render_to_response(template, context, RequestContext(request))


def corpmembership_search(request,
            template_name="corporate_memberships/applications/search.html"):
    allow_anonymous_search = get_setting('module',
                                     'corporate_memberships',
                                     'anonymoussearchcorporatemembers')

    if not request.user.is_authenticated() and not allow_anonymous_search:
        raise Http403

    search_form = CorpMembershipSearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data['q']
        cm_id = search_form.cleaned_data['cm_id']
        try:
            cm_id = int(cm_id)
        except:
            pass
    else:
        query = None
        cm_id = None

    if query == 'is_pending:true' and request.user.profile.is_superuser:
        # pending list only for admins
        q_obj = Q(status_detail__in=['pending', 'paid - pending approval'])
        corp_members = CorpMembership.objects.filter(q_obj)
    else:
        filter_and, filter_or = CorpMembership.get_search_filter(request.user)

        q_obj = None
        if filter_and:
            q_obj = Q(**filter_and)
        if filter_or:
            q_obj_or = reduce(operator.or_, [Q(**{key: value}
                        ) for key, value in filter_or.items()])
            if q_obj:
                q_obj = reduce(operator.and_, [q_obj, q_obj_or])
            else:
                q_obj = q_obj_or

        if query:
            corp_members = CorpMembership.objects.filter(
                                corp_profile__name__icontains=query)
        else:
            corp_members = CorpMembership.objects.all()
        if q_obj:
            corp_members = corp_members.filter(q_obj)

    if cm_id:
        corp_members = corp_members.filter(id=cm_id)
    corp_members = corp_members.order_by('corp_profile__name')

    EventLog.objects.log()

    return render_to_response(template_name, {
        'corp_members': corp_members,
        'search_form': search_form},
        context_instance=RequestContext(request))


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
            EventLog.objects.log()
            corp_profile = corp_memb.corp_profile
            corp_memb.delete()
            # delete the corp profile if none of the corp memberships
            # associating with it.
            if not corp_profile.corp_memberships.all():
                corp_profile.delete()

            return HttpResponseRedirect(reverse('corpmembership.search'))

        return render_to_response(template_name, {'corp_memb': corp_memb},
            context_instance=RequestContext(request))
    else:
        raise Http403


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


@login_required
def corp_renew(request, id,
               template='corporate_memberships/renewal.html'):
    corp_membership = get_object_or_404(CorpMembership, id=id)
    new_corp_membership = corp_membership.copy()

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


def corp_renew_conf(request, id,
                    template="corporate_memberships/renewal_conf.html"):
    corp_membership = get_object_or_404(CorpMembership, id=id)

    if not has_perm(request.user,
                    'corporate_memberships.change_corporatemembership',
                    corp_membership):
        if not corp_membership.allow_edit_by(request.user):
            raise Http403

    corpmembership_app = CorpMembershipApp.objects.current_app()

    EventLog.objects.log(instance=corp_membership)
    context = {"corp_membership": corp_membership,
               'corp_profile': corp_membership.corp_profile,
               'corp_app': corpmembership_app,
               }
    return render_to_response(template, context, RequestContext(request))


@login_required
def roster_search(request,
                  template_name='corporate_memberships/roster_search.html'):
    form = RosterSearchAdvancedForm(request.GET or None)
    if form.is_valid():
        # cm_id - CorpMembership id
        cm_id = form.cleaned_data['cm_id']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        search_criteria = form.cleaned_data['search_criteria']
        search_text = form.cleaned_data['search_text']
        search_method = form.cleaned_data['search_method']
    else:
        cm_id = None
        first_name = None
        last_name = None
        email = None
        search_criteria = None
        search_text = None
        search_method = None
    if cm_id:
        [corp_membership] = CorpMembership.objects.filter(
                                    id=cm_id).exclude(
                                    status_detail='archive'
                                            )[:1] or [None]
    else:
        corp_membership = None

    # check for membership permissions
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
        filter_and.update({'user__first_name': first_name})
    if last_name:
        filter_and.update({'user__last_name': last_name})
    if email:
        filter_and.update({'user__email': email})
    search_type = ''
    if search_method == 'starts_with':
        search_type = '__startswith'
    elif search_method == 'contains':
        search_type = '__contains'

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
                                  'form': form},
            context_instance=RequestContext(request))


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

    title_list = corp_profile_field_list + corp_memb_field_list \
                     + base_field_list

    return render_csv(filename, title_list, [])


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
                               in CorpMembership._meta.fields \
                             if not field.__class__ == AutoField]
            corp_memb_field_list.remove('guid')
            corp_memb_field_list.remove('corp_profile')

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


def corp_reps_lookup(request):
    q = request.REQUEST['term']

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


def index(request,
          template_name="corporate_memberships/applications/index.html"):
    corp_app = CorpMembershipApp.objects.current_app()
    EventLog.objects.log()

    return render_to_response(template_name, {'corp_app': corp_app},
        context_instance=RequestContext(request))


@staff_member_required
def summary_report(request,
                template_name='corporate_memberships/reports/summary.html'):
    """
    Shows a report of corporate memberships per corporate membership type.
    """
    summary, total = get_corp_memb_summary()

    EventLog.objects.log()

    return render_to_response(template_name, {
        'summary': summary,
        'total': total,
        }, context_instance=RequestContext(request))


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
    
    field_objs = list(field_objs.order_by('order'))
    
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


def add_conf(request, id, template="corporate_memberships/add_conf.html"):
    """
        add a corporate membership
    """ 
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
#    if not has_perm(request.user,'corporate_memberships.view_corporatemembership',corporate_membership):
#        raise Http403
    EventLog.objects.log(instance=corporate_membership)
    context = {"corporate_membership": corporate_membership}
    return render_to_response(template, context, RequestContext(request))

@login_required
def edit(request, id, template="corporate_memberships/edit.html"):
    """
        edit a corporate membership
    """ 
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    if not has_perm(request.user,'corporate_memberships.change_corporatemembership',corporate_membership):
        if not corporate_membership.allow_edit_by(request.user):
            raise Http403
    
    user_is_superuser = request.user.profile.is_superuser
    
    corp_app = corporate_membership.corp_app
    
    # get the list of field objects for this corporate membership
    field_objs = corp_app.fields.filter(visible=1)
    if not user_is_superuser:
        field_objs = field_objs.filter(admin_only=0)
    
    field_objs = list(field_objs.order_by('order'))
    
    # get the field entry for each field_obj if exists
    for field_obj in field_objs:
        field_obj.entry = field_obj.get_entry(corporate_membership)
        field_obj.display_only = False
        
        # make corporate_membership_type and payment_method as the display_only fields
        # because we're not allowing them to edit those fields
        if field_obj.field_name in ['corporate_membership_type', 'payment_method']:
            field_obj.display_only = True
            if field_obj.field_name == 'corporate_membership_type':
                field_obj.display_content = corporate_membership.corporate_membership_type.name
                
            if field_obj.field_name == 'payment_method':
                field_obj.display_content = corporate_membership.payment_method
                if corporate_membership.invoice:
                    field_obj.display_content = '%s - <a href="%s">View Invoice</a>' % (field_obj.display_content,
                                                                                        corporate_membership.invoice.get_absolute_url())
        
    form = CorpMembForm(corporate_membership.corp_app, field_objs, request.POST or None, 
                        request.FILES or None, instance=corporate_membership)
    
    # add or delete fields based on the security level
    if user_is_superuser:
        field_objs.append(CorpField(label='Admin Only', field_type='section_break', admin_only=1))
        field_objs.append(CorpField(label='Join Date', field_name='join_dt', admin_only=1))
        field_objs.append(CorpField(label='Expiration Date', 
                                    field_name='expiration_dt', 
                                    admin_only=1))
        field_objs.append(CorpField(label='Status', field_name='status', admin_only=1))
        field_objs.append(CorpField(label='status_detail', field_name='status_detail', admin_only=1))
    else:
        del form.fields['join_dt']
        del form.fields['expiration_dt']
        del form.fields['status']
        del form.fields['status_detail']
       
    
#    # corporate_membership_type choices
#    form.fields['corporate_membership_type'].choices = get_corporate_membership_type_choices(request.user, 
#                                                                                corp_app)
#    
#    form.fields['payment_method'].choices = get_payment_method_choices(request.user, corp_app)
    
    # we don't need the captcha on edit because it requires login
    #del form.fields['captcha']
    
    status_info_before_edit = {'corporate_membership_type': corporate_membership.corporate_membership_type,
                               'status': corporate_membership.status,
                               'status_detail': corporate_membership.status_detail}
    old_corp_memb = CorporateMembership.objects.get(pk=corporate_membership.pk)
        
    if request.method == "POST":
        if form.is_valid():
            corporate_membership = form.save(request.user, commit=False)
            # archive the corporate membership if any of these changed:
            # corporate_membership_type, status, status_detail
            need_archive = False
            for key in status_info_before_edit:
                value = getattr(corporate_membership, key)

                if value != status_info_before_edit[key]:
                    need_archive = True
                    break
            if need_archive:
                old_corp_memb.archive(request.user)
            corporate_membership.save()
            corp_memb_update_perms(corporate_membership)
            
            # send notification to administrators
            if not user_is_superuser:
                recipients = get_notice_recipients('module', 'corporate_membership', 'corporatemembershiprecipients')
                extra_context = {
                    'object': corporate_membership,
                    'request': request,
                }
                send_email_notification('corp_memb_edited', recipients, extra_context)

            return HttpResponseRedirect(reverse('corp_memb.view', args=[corporate_membership.id]))
            
            
    
    context = {"corporate_membership": corporate_membership, 
               'corp_app': corp_app,
               'field_objs': field_objs, 
               'form':form}
    return render_to_response(template, context, RequestContext(request))

@login_required
def renew(request, id, template="corporate_memberships/renew.html"):
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    if not has_perm(request.user,'corporate_memberships.change_corporatemembership',corporate_membership):
        if not corporate_membership.allow_edit_by(request.user):
            raise Http403
        
    if corporate_membership.is_renewal_pending:
        messages.add_message(request, messages.INFO, 'The corporate membership "%s" has been renewed and is pending for admin approval.' % corporate_membership.name)
        return HttpResponseRedirect(reverse('corp_memb.view', args=[corporate_membership.id]))
        
    user_is_superuser = request.user.profile.is_superuser
    
    corp_app = corporate_membership.corp_app
    
    form = CorpMembRenewForm(request.POST or None, user=request.user, corporate_membership=corporate_membership)
    
    if request.method == "POST":
        if form.is_valid():
            if 'update_summary' in request.POST:
                pass
            else:
                
                members = form.cleaned_data['members']
                
                corp_renew_entry = form.save(commit=False)
                corp_renew_entry.corporate_membership = corporate_membership
                corp_renew_entry.creator = request.user
                corp_renew_entry.status_detail = 'pending'
                corp_renew_entry.save()
                
                # calculate the total price for invoice
                corp_renewal_price = corp_renew_entry.corporate_membership_type.renewal_price
                if not corp_renewal_price:
                    corp_renewal_price = 0
                indiv_renewal_price = corp_renew_entry.corporate_membership_type.membership_type.renewal_price
                if not indiv_renewal_price:
                    indiv_renewal_price = 0
                
                renewal_total = corp_renewal_price + indiv_renewal_price * len(members)
                opt_d = {'renewal':True, 
                         'renewal_total': renewal_total,
                         'renew_entry':corp_renew_entry}
                # create an invoice - invoice.object_type - use corporate_membership?
                inv = corp_memb_inv_add(request.user, corporate_membership, **opt_d)
                
                # update corp_renew_entry with inv
                corp_renew_entry.invoice = inv
                corp_renew_entry.save()
                
                corporate_membership.renew_entry_id = corp_renew_entry.id
                corporate_membership.save()
                
                # store individual members
                for id in members:
                    membership = Membership.objects.first(id=id)
                    ind_memb_renew_entry = IndivMembRenewEntry(corp_memb_renew_entry=corp_renew_entry,
                                                               membership=membership)
                    ind_memb_renew_entry.save()

                # handle online payment
                if corp_renew_entry.get_payment_method().is_online:
                #if corp_renew_entry.payment_method.lower() in ['credit card', 'cc']:
                    if corp_renew_entry.invoice and corp_renew_entry.invoice.balance > 0:
                        return HttpResponseRedirect(reverse('payment.pay_online', 
                                                            args=[corp_renew_entry.invoice.id, 
                                                                  corp_renew_entry.invoice.guid]))
                        
                extra_context = {
                    'object': corporate_membership,
                    'request': request,
                    'corp_renew_entry': corp_renew_entry,
                    'invoice': inv,
                }
                if user_is_superuser:
                    # admin: approve renewal
                    corporate_membership.approve_renewal(request)
                else:
                    # send a notice to admin
                    recipients = get_notice_recipients('module', 'corporate_memberships', 'corporatemembershiprecipients')
                    
                    send_email_notification('corp_memb_renewed', recipients, extra_context)
                    
                   
                            
                # send an email to dues reps
                recipients = dues_rep_emails_list(corporate_membership)
                send_email_notification('corp_memb_renewed_user', recipients, extra_context)
                    
                    
                return HttpResponseRedirect(reverse('corp_memb.renew_conf', args=[corporate_membership.id]))
                
    
    
    summary_data = {'corp_price':0, 'individual_price':0, 'individual_count':0, 
                    'individual_total':0, 'total_amount':0}
    if corporate_membership.corporate_membership_type.renewal_price == 0:
        summary_data['individual_count'] = len(get_indiv_membs_choices(corporate_membership))

    if request.method == "POST":
        cmt_id = request.POST.get('corporate_membership_type', 0)
        try:
            cmt = CorporateMembershipType.objects.get(id=cmt_id)
        except CorporateMembershipType.DoesNotExist:
            pass
        summary_data['individual_count'] = len(request.POST.getlist('members'))
    else:
        cmt = corporate_membership.corporate_membership_type
    
    if cmt:
        summary_data['corp_price'] = cmt.renewal_price
        if not summary_data['corp_price']:
            summary_data['corp_price'] = 0
        summary_data['individual_price'] = cmt.membership_type.renewal_price
        if not summary_data['individual_price']:
            summary_data['individual_price'] = 0
    summary_data['individual_total'] = summary_data['individual_count'] * summary_data['individual_price']
    summary_data['total_amount'] = summary_data['individual_total'] + summary_data['corp_price']
    
    context = {"corporate_membership": corporate_membership, 
               'corp_app': corp_app,
               'form': form,
               'summary_data': summary_data,
               }
    return render_to_response(template, context, RequestContext(request))

@login_required
def renew_conf(request, id, template="corporate_memberships/renew_conf.html"):
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    if not has_perm(request.user,'corporate_memberships.change_corporatemembership',corporate_membership):
        if not corporate_membership.allow_edit_by(request.user):
            raise Http403
        
    #user_is_superuser = request.user.profile.is_superuser
    
    corp_app = corporate_membership.corp_app
    
    try:
        renew_entry = CorpMembRenewEntry.objects.get(pk=corporate_membership.renew_entry_id)
    except CorpMembRenewEntry.DoesNotExist:
        renew_entry = None

    EventLog.objects.log(instance=corporate_membership)
    context = {"corporate_membership": corporate_membership, 
               'corp_app': corp_app,
               'renew_entry': renew_entry,
               }
    return render_to_response(template, context, RequestContext(request))


@login_required
def approve(request, id, template="corporate_memberships/approve.html"):
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    user_is_superuser = request.user.profile.is_superuser
    if not user_is_superuser:
        raise Http403
    
    # if not in pending, go to view page
    if not (corporate_membership.is_pending):
        return HttpResponseRedirect(reverse('corp_memb.view', args=[corporate_membership.id]))

    try:
        renew_entry = CorpMembRenewEntry.objects.get(pk=corporate_membership.renew_entry_id)
    except CorpMembRenewEntry.DoesNotExist:
        renew_entry = None
        
    if renew_entry:
        indiv_renew_entries = renew_entry.indiv_memb_renew_entries()
        corp_membership_type = renew_entry.corporate_membership_type
        new_expiration_dt = corp_membership_type.get_expiration_dt(renewal=True,
                                                join_dt=corporate_membership.join_dt,
                                                renew_dt=renew_entry.create_dt)
    else:
        indiv_renew_entries = None
        corp_membership_type = corporate_membership.corporate_membership_type
        new_expiration_dt = corp_membership_type.get_expiration_dt(renewal=False,
                                                join_dt=corporate_membership.join_dt,
                                                renew_dt=corporate_membership.create_dt)
        
    approve_form = CorpApproveForm(request.POST or None, corporate_membership=corporate_membership)
    if request.method == "POST":
        if approve_form.is_valid():
            msg = ''
            if 'approve' in request.POST:
                if renew_entry:
                    # approve the renewal
                    corporate_membership.approve_renewal(request)
                   
                    msg = 'Corporate membership "%s" renewal has been APPROVED.' % corporate_membership.name
                    
                    event_id = 682002
                    event_data = '%s (%d) renewal approved by %s' % (corporate_membership._meta.object_name, 
                                                                     corporate_membership.pk, request.user)
                    event_description = '%s renewal approved' % corporate_membership._meta.object_name
                    
                else:
                    # approve join
                    params = {'create_new': True,
                              'assign_to_user': None}
                    if approve_form.fields and corporate_membership.anonymous_creator:
                        user_pk = int(approve_form.cleaned_data['users'])
                        if user_pk:
                            try:
                                params['assign_to_user'] = User.objects.get(pk=user_pk)
                                params['create_new'] = False
                            except User.DoesNotExist:
                                pass  

                    corporate_membership.approve_join(request, **params)
                    
                    msg = 'Corporate membership "%s" has been APPROVED.' % corporate_membership.name
                    event_id = 682001
                    event_data = '%s (%d) approved by %s' % (corporate_membership._meta.object_name, 
                                                            corporate_membership.pk, request.user)
                    event_description = '%s approved' % corporate_membership._meta.object_name
            else:
                if 'disapprove' in request.POST:
                    if renew_entry:
                        # deny the renewal
                        corporate_membership.disapprove_renewal(request)
                        
                        msg = 'Corporate membership "%s" renewal has been DENIED.' % corporate_membership.name
                        event_id = 682004
                        event_data = '%s (%d) renewal denied by %s' % (corporate_membership._meta.object_name, 
                                                                     corporate_membership.pk, request.user)
                        event_description = '%s renewal denied' % corporate_membership._meta.object_name
                    else:
                        # deny join
                        corporate_membership.disapprove_join(request)
                        msg = 'Corporate membership "%s" has been DENIED.' % corporate_membership.name
                        event_id = 682003
                        event_data = '%s (%d) denied by %s' % (corporate_membership._meta.object_name, 
                                                            corporate_membership.pk, request.user)
                        event_description = '%s denied' % corporate_membership._meta.object_name
                    
            if msg:      
                messages.add_message(request, messages.SUCCESS, msg)

            EventLog.objects.log(instance=corporate_membership)

            return HttpResponseRedirect(reverse('corp_memb.view', args=[corporate_membership.id]))
    
    
    context = {"corporate_membership": corporate_membership,
               'renew_entry': renew_entry,
               'indiv_renew_entries': indiv_renew_entries,
               'new_expiration_dt': new_expiration_dt,
               'approve_form': approve_form,
               }
    return render_to_response(template, context, RequestContext(request))
    
    

def view(request, id, template="corporate_memberships/view.html"):
    """
        view a corporate membership
    """  
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    corporate_membership.status_detail = corporate_membership.real_time_status_detail
    
    if not has_perm(request.user, 'corporate_memberships.view_corporatemembership', corporate_membership):
        if not corporate_membership.allow_view_by(request.user):
            raise Http403
    
    can_edit = False
    if has_perm(request.user, 'corporate_memberships.change_corporatemembership', corporate_membership):
        can_edit = True
    
    user_is_superuser = request.user.profile.is_superuser
    
    field_objs = corporate_membership.corp_app.fields.filter(visible=1)
    if not user_is_superuser:
        field_objs = field_objs.filter(admin_only=0)
    if not can_edit:
        field_objs = field_objs.exclude(field_name='corporate_membership_type')
    
    field_objs = list(field_objs.order_by('order'))
    
    if can_edit:
        field_objs.append(CorpField(label='Representatives', field_type='section_break', admin_only=0))
        field_objs.append(CorpField(label='Reps', field_name='reps', object_type='corporate_membership', admin_only=0))
        
    if user_is_superuser:
        field_objs.append(CorpField(label='Admin Only', field_type='section_break', admin_only=1))
        field_objs.append(CorpField(label='Join Date', field_name='join_dt', object_type='corporate_membership', admin_only=1))
        field_objs.append(CorpField(label='Expiration Date', field_name='expiration_dt', object_type='corporate_membership', admin_only=1))
        field_objs.append(CorpField(label='Status', field_name='status', object_type='corporate_membership', admin_only=1))
        field_objs.append(CorpField(label='Status Detail', field_name='status_detail', object_type='corporate_membership', admin_only=1))
        
    for field_obj in field_objs:
        field_obj.value = field_obj.get_value(corporate_membership)
        if isinstance(field_obj.value, datetime) or isinstance(field_obj.value, date):
            field_obj.is_date = True
        else:
            field_obj.is_date = False
            
    EventLog.objects.log(instance=corporate_membership)
    context = {"corporate_membership": corporate_membership, 'field_objs': field_objs}
    return render_to_response(template, context, RequestContext(request))


def search(request, template_name="corporate_memberships/search.html"):
    allow_anonymous_search = get_setting('module', 
                                     'corporate_memberships', 
                                     'anonymoussearchcorporatemembers')

    if not request.user.is_authenticated() and not allow_anonymous_search:
        raise Http403
    
    query = request.GET.get('q', None)
    
    if query == 'is_pending:true' and request.user.profile.is_superuser:
        # pending list only for admins
        pending_rew_entry_ids = CorpMembRenewEntry.objects.filter(
                                    status_detail__in=['pending', 'paid - pending approval']
                                    ).values_list('id', flat=True)
        q_obj = Q(status_detail__in=['pending', 'paid - pending approval'])
        if pending_rew_entry_ids:
            q_obj = q_obj | Q(renew_entry_id__in=pending_rew_entry_ids)
        corp_members = CorporateMembership.objects.filter(q_obj)
    else:
    
        filter_and, filter_or = CorporateMembership.get_search_filter(request.user)
        q_obj = None
        if filter_and:
            q_obj = Q(**filter_and)
        if filter_or:
            q_obj_or = reduce(operator.or_, [Q(**{key: value}) for key, value in filter_or.items()])
            if q_obj:
                q_obj = reduce(operator.and_, [q_obj, q_obj_or])
            else:
                q_obj = q_obj_or
        
        if get_setting('site', 'global', 'searchindex') and query:
            corp_members = CorporateMembership.objects.search(query, user=request.user)
            if q_obj:
                corp_members = corp_members.filter(q_obj)
            corp_members = corp_members.order_by('name_exact')
        else:
            if q_obj:
                corp_members = CorporateMembership.objects.filter(q_obj)
            else:
                corp_members = CorporateMembership.objects.all()
        
    #        if request.user.is_authenticated():
    #            corp_members = corp_members.select_related()
            
        
    corp_members = corp_members.order_by('name')

    EventLog.objects.log()

    return render_to_response(template_name, {'corp_members': corp_members}, 
        context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="corporate_memberships/delete.html"):
    corp_memb = get_object_or_404(CorporateMembership, pk=id)

    if has_perm(request.user,'corporate_memberships.delete_corporatemembership'):   
        if request.method == "POST":
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % corp_memb)
            
#            # send notification to administrators
#            recipients = get_notice_recipients('module', 'corporate_membership', 'corporatemembershiprecipients')
#            if recipients:
#                if notification:
#                    extra_context = {
#                        'object': corp_memb,
#                        'request': request,
#                    }
#                    notification.send_emails(recipients,'corp_memb_deleted', extra_context)
#            
            corp_memb.delete()
                
            return HttpResponseRedirect(reverse('corp_memb.search'))
    
        return render_to_response(template_name, {'corp_memb': corp_memb}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
    
def edit_reps(request, id, form_class=CorpMembRepForm, template_name="corporate_memberships/edit_reps.html"):
    corp_memb = get_object_or_404(CorporateMembership, pk=id)
    
    if not has_perm(request.user,'corporate_memberships.change_corporatemembership',corp_memb):
        raise Http403
    
    reps = CorporateMembershipRep.objects.filter(corporate_membership=corp_memb).order_by('user')
    form = form_class(corp_memb, request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            rep = form.save(commit=False)
            rep.corporate_membership = corp_memb
            rep.save()
            
            corp_memb_update_perms(corp_memb)
            
            # this is to update the search index for corporate memberships
            if use_search_index:
                corp_memb.save()
            
            # log an event here
            
            if (request.POST.get('submit', '')).lower() == 'save':
                return HttpResponseRedirect(reverse('corp_memb.view', args=[corp_memb.id]))
    
    if use_search_index:        
        memberships = Membership.objects.corp_roster_search(None, 
                                                user=request.user).filter(
                                            corporate_membership_id=corp_memb.id)
    else:
        memberships = Membership.objects.active(corporate_membership_id=corp_memb.id)
    try:
        page = int(request.GET.get('page', 0))
    except:
        page = 0
    
    return render_to_response(template_name, {'corp_memb': corp_memb, 
                                              'form': form,
                                              'reps': reps,
                                              'memberships': memberships,
                                              'page': page}, 
        context_instance=RequestContext(request))
    
def reps_lookup(request):
    q = request.REQUEST['term']
    
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
    
@login_required
def delete_rep(request, id, template_name="corporate_memberships/delete_rep.html"):
    rep = get_object_or_404(CorporateMembershipRep, pk=id)
    corp_memb = rep.corporate_membership

    if corp_memb.allow_edit_by(request.user) or \
         has_perm(request.user,'corporate_memberships.edit_corporatemembership'):   
        if request.method == "POST":
            
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % rep)
            
            rep.delete()
            corp_memb_update_perms(corp_memb)
            
            # this is to update the search index for corporate memberships
            if use_search_index:
                corp_memb.save()
                
            return HttpResponseRedirect(reverse('corp_memb.edit_reps', args=[corp_memb.pk]))
    
        return render_to_response(template_name, {'corp_memb': corp_memb}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
  
    
@staff_member_required
@password_required
def corp_import(request, step=None):
    """
    Corporate membership import.
    """
    #if not request.user.profile.is_superuser:  # admin only page
    #    raise Http403

    if not step:  # start from beginning
        return redirect('corp_memb_import_upload_file')
    
    request.session.set_expiry(0)  # expire when browser is closed
    step_numeral, step_name = step

    if step_numeral == 1:  # upload-file
        template_name = 'corporate_memberships/import/upload_file.html'
        err_msg = ""
        if request.method == 'POST':
            form = CSVForm(request.POST, request.FILES, step=step)
            if form.is_valid():
                cleaned_data = form.save(step=step)
                corp_app = cleaned_data['corp_app']

                # check import requirements
                saved_files = File.objects.save_files_for_instance(request, CorporateMembership)
                #file_path = os.path.join(settings.MEDIA_ROOT, str(saved_files[0].file))
                file_path = str(saved_files[0].file)
                is_valid_import, missing_required_fields = validate_import_file(file_path)
                
                if is_valid_import:
                    # store session info
                    request.session['corp_memb.import.corp_app'] = corp_app
                    request.session['corp_memb.import.file_path'] = file_path
                    request.session['corp_memb.import.update_option'] = cleaned_data['update_option']
            
                    # move to next wizard page
                    return redirect('corp_memb_import_map_fields')
                else:
                    err_msg = 'The CSV File is missing required field(s): %s' % (', '.join(missing_required_fields))
        else:  # if not POST
            form = CSVForm(step=step)

        return render_to_response(template_name, {
            'form':form,
            'datetime':datetime,
            'err_msg': err_msg
            }, context_instance=RequestContext(request))
        
    if step_numeral == 2:  # map-fields
        template_name = 'corporate_memberships/import/map_fields.html'
        file_path = request.session.get('corp_memb.import.file_path')
        corp_app = request.session.get('corp_memb.import.corp_app')
        update_option = request.session.get('corp_memb.import.update_option')
        
        if not all([corp_app, file_path, update_option]):
            return redirect('corp_memb_import_upload_file')

        if request.method == 'POST':
            form = CSVForm(
                request.POST,
                request.FILES,
                step=step,
                corp_app=corp_app,
                file_path=file_path
            )

            if form.is_valid():
                cleaned_data = form.save(step=step)
                file_path = request.session.get('corp_memb.import.file_path')

                corp_membs = new_corp_mems_from_csv(request, file_path, corp_app, cleaned_data, update_option)

                request.session['corp_memb.import.corp_membs'] = corp_membs
                request.session['corp_memb.import.fields'] = cleaned_data

                return redirect('corp_memb_import_preview')

        else:  # if not POST
            form = CSVForm(step=step, corp_app=corp_app, file_path=file_path)

        return render_to_response(template_name, {
            'form':form,
            'datetime':datetime,
            }, context_instance=RequestContext(request))
        
    if step_numeral == 3:  # preview
        template_name = 'corporate_memberships/import/preview.html'
        corp_membs = request.session.get('corp_memb.import.corp_membs')
        update_option = request.session.get('corp_memb.import.update_option')
        if not all([corp_membs, update_option]):
            return redirect('corp_memb_import_upload_file')

        added, skipped, updated, updated_override, invalid_skipped = [], [], [], [], []
        for corp_memb in corp_membs:
            if not corp_memb.is_valid:
                invalid_skipped.append(corp_memb)
            else:
                if corp_memb.pk:
                    if update_option == 'skip': 
                        skipped.append(corp_memb)
                    else:
                        if update_option == 'update':
                            updated.append(corp_memb)
                        else:
                            updated_override.append(corp_memb)
                else: 
                    added.append(corp_memb)

        return render_to_response(template_name, {
        'corp_membs':corp_membs,
        'added': added,
        'update_option': update_option,
        'invalid_skipped': invalid_skipped,
        'skipped': skipped,
        'updated': updated,
        'updated_override': updated_override,
        'datetime': datetime,
        }, context_instance=RequestContext(request))
        
    if step_numeral == 4:  # confirm
        template_name = 'corporate_memberships/import/confirm.html'

        corp_app = request.session.get('corp_memb.import.corp_app')
        corp_membs = request.session.get('corp_memb.import.corp_membs')
        fields_dict = request.session.get('corp_memb.import.fields')
        update_option = request.session.get('corp_memb.import.update_option')
        file_path = request.session.get('corp_memb.import.file_path')

        if not all([corp_app, corp_membs, fields_dict]):
            return redirect('corp_memb_import_upload_file')

        added, skipped, updated, updated_override, invalid_skipped = [], [], [], [], []
        field_keys = [item[0] for item in fields_dict.items() if item[1]]
        
        for corp_memb in corp_membs:
            if not corp_memb.is_valid:
                invalid_skipped.append(corp_memb)
                
                continue
            
            is_insert = False
            if not corp_memb.pk: 
                corp_memb.save()  # create pk
                is_insert = True
                added.append(corp_memb)
            else:
                if update_option == 'skip': 
                    skipped.append(corp_memb)
                else:
                    if update_option == 'update':
                        updated.append(corp_memb)
                    else:
                        updated_override.append(corp_memb)
                        
                    corp_memb.save()
                        
            if not is_insert and update_option == 'skip':
                continue
                
            # take care of authorized_domains and dues_rep
            # and add custom fields to the field entry
            for field_key in field_keys:
                if not hasattr(corp_memb, field_key):
                    if field_key in ['authorized_domains', 'dues_rep']:
                        if field_key == 'authorized_domains':
                            # if auth domains exist for this corp memb
                            #     if update_option == 'update', skip
                            #     if update_option == 'override',
                            #            1) delete existing auth domains
                            if not is_insert:
                                existing_auth_domains = AuthorizedDomain.objects.filter(
                                                        corporate_membership=corp_memb)
                                if existing_auth_domains:
                                    if update_option == 'update':
                                        continue
                                    elif update_option == 'override':
                                        # delete existing auth domains
                                        for auth_domain in existing_auth_domains:
                                            auth_domain.delete()
                                    
                            # add new auth domains
                            domains = (corp_memb.cm[field_key]).split(',')
                            domains = [domain.strip() for domain in domains]
                            for domain in domains:
                                AuthorizedDomain.objects.create(
                                         corporate_membership=corp_memb,
                                         name= domain      
                                                            )
                        if field_key == 'dues_rep':
                            # same as auth domains, check for existing dues reps
                            if not is_insert:
                                existing_dues_reps = CorporateMembershipRep.objects.filter(
                                                                corporate_membership=corp_memb,
                                                                is_dues_rep=True
                                                                    )
                                if existing_dues_reps:
                                    if update_option == 'update':
                                        continue
                                    elif update_option == 'override':
                                        # delete existing auth domains
                                        for dues_rep in existing_dues_reps:
                                            dues_rep.delete()
                            
                            # add new dues_reps
                            usernames = (corp_memb.cm[field_key]).split(',')
                            usernames = [username.strip() for username in usernames]
                            for username in usernames:
                                try:
                                    tmp_user = User.objects.get(username=username)
                                except User.DoesNotExist:
                                    continue
                                
                                CorporateMembershipRep.objects.create(
                                                            corporate_membership=corp_memb,
                                                            user=tmp_user,
                                                            is_dues_rep=True
                                                                      )
                            
                    else:
                        # custom field - field_key should have the pattern field_id
                        field_id = field_key.replace('field_', '')
                        try:
                            field_id = int(field_id)
                        except:
                            continue # skip if field doesn't exist
                        
                        try:
                            corp_field = CorpField.objects.get(pk=field_id)
                        except CorpField.DoesNotExist:
                            continue    # skip if field doesn't exist
                        
                        
                        # if this custom field entry exists
                        #     if update_option == 'update', skip
                        #     if update_option == 'override',
                        #            1) override the value
                        add_custom_field = False
                        if is_insert:
                            add_custom_field = True
                        else: # not is_insert:
                            try:
                                cfe = CorpFieldEntry.objects.get(
                                        corporate_membership=corp_memb,
                                        field=corp_field          
                                                                 )
                                if update_option == 'update' and cfe.value:
                                    continue
                                else:
                                    cfe.value =corp_memb.cm[field_key]
                                    cfe.save() 
                                    
                            except CorpFieldEntry.DoesNotExist:
                                add_custom_field = True
                                
                        if add_custom_field:
                            CorpFieldEntry.objects.create(
                                        corporate_membership=corp_memb,
                                        field=corp_field,
                                        value=corp_memb.cm[field_key]               
                                                         )
                            
        if invalid_skipped:
            request.session['corp_memb.import.invalid_skipped'] = invalid_skipped
            
        
        # we're done. clear the session variables related to this import
        del request.session['corp_memb.import.corp_app']
        del request.session['corp_memb.import.corp_membs']
        del request.session['corp_memb.import.fields']
        del request.session['corp_memb.import.update_option']
        
        total_added = len(added)
        total_updated = len(updated) + len(updated_override)
        totals = total_added + total_updated

        EventLog.objects.log()

        return render_to_response(template_name, {
            'corp_membs': corp_membs,
            'update_option': update_option,
            'invalid_skipped': invalid_skipped,
            'added': added,
            'skipped': skipped,
            'updated': updated,
            'updated_override': updated_override,
            'datetime': datetime,
        }, context_instance=RequestContext(request))
        
@staff_member_required
def download_csv_import_template(request, file_ext='.csv'):
    from django.db.models.fields import AutoField
    #if not request.user.profile.is_superuser:raise Http403   # admin only page
    
    filename = "corporate_memberships_import.csv"
    
    corp_memb_field_names = [smart_str(field.name) for field in CorporateMembership._meta.fields 
                             if field.editable and (not field.__class__==AutoField)]
   
    fields_to_exclude = ['guid',
                         'allow_anonymous_view',
                         'allow_user_view',
                         'allow_member_view',
                         'allow_user_edit',
                         'allow_member_edit',
                         'creator_username',
                         'owner',
                         'owner_username',
                         'renew_entry_id',
                         'approved_denied_dt',
                         'approved_denied_user',
                         'payment_method',
                         'invoice',
                         'corp_app',
                         'status',
                         'status_detail'
                         ]
    for field in fields_to_exclude:
        if field in corp_memb_field_names:
            corp_memb_field_names.remove(field)
            
    corp_memb_field_names.extend(['authorized_domains', 'dues_rep'])
    
            
    data_row_list = []
    EventLog.objects.log()

    return render_excel(filename, corp_memb_field_names, data_row_list, file_ext)

@staff_member_required
def corp_import_invalid_records_download(request):
    
    #if not request.user.profile.is_superuser:raise Http403   # admin only page
    
    file_path = request.session.get('corp_memb.import.file_path')
    invalid_corp_membs = request.session.get('corp_memb.import.invalid_skipped')
    #print invalid_corp_membs
    
    if not file_path or not invalid_corp_membs:
        raise Http403
    
    data = csv.reader(default_storage.open(file_path, 'rU'))
    title_fields = data.next()
    title_fields = [smart_str(field) for field in title_fields]
    
    item_list = []
    for corp_memb in invalid_corp_membs:
        item = []
        for field in title_fields:
            value = corp_memb.cm.get(field)
            if not value: value = ' '
            item.append(value)
            
        if item:
            item.append('\n')
            item.insert(0, corp_memb.err_msg)
            item_list.append(item)
            
    title_fields.append('\n')
    title_fields.insert(0, 'Invalid Reason?')
    
    filebase, filename = os.path.split(file_path)
    filename = "Invalid_records_%s" % filename
    
    # clear the session now
    #del request.session['corp_memb.import.file_path']
    #del request.session['corp_memb.import.invalid_skipped']
    EventLog.objects.log()

    return render_excel(filename, title_fields, item_list, '.csv')

@login_required
@password_required
def corp_export(request):
    if not request.user.profile.is_superuser:raise Http403   # admin only page
    
    template_name = 'corporate_memberships/export.html'
    form = ExportForm(request.POST or None, user=request.user)
    
    if request.method == 'POST':
        if form.is_valid():
            # reset the password_promt session
            request.session['password_promt'] = False
            corp_app = form.cleaned_data['corp_app']
            
            filename = "corporate_memberships_%d_export.csv" % corp_app.id
            
            corp_fields = CorpField.objects.filter(corp_app=corp_app).exclude(field_type__in=('section_break', 
                                                               'page_break')).order_by('order')
            label_list = [corp_field.label for corp_field in corp_fields]
            extra_field_labels = ['Dues reps', 'Join Date', 'Expiration Date', 'Status', 'Status Detail', 'Invoice Number', 'Invoice Amount', 'Invoice Balance']
            extra_field_names = ['dues_reps', 'join_dt', 'expiration_dt', 'status', 'status_detail', 'invoice_id', 'total', 'balance']
            
            label_list.extend(extra_field_labels)
            label_list.append('\n')
            
            data_row_list = []
            corp_membs = CorporateMembership.objects.all()
            for corp_memb in corp_membs:
                data_row = []
                field_entries = CorpFieldEntry.objects.filter(corporate_membership=corp_memb).values('field', 'value')
                field_entries_d = {}
                for entry in field_entries:
                    field_entries_d[entry['field']] = entry['value']
                for corp_field in corp_fields:
                    value = ''
                    if corp_field.field_name and corp_field.object_type == 'corporate_membership':
                        if corp_field.field_name in ['corporate_membership_type',
                                                     'authorized_domains',
                                                     'payment_method']:
                            if corp_field.field_name == "corporate_membership_type":
                                value = corp_memb.corporate_membership_type.name
                            elif corp_field.field_name == "authorized_domains":
                                auth_domains = AuthorizedDomain.objects.filter(corporate_membership=corp_memb)
                                value = '; '.join([auth_domain.name for auth_domain in auth_domains])
                            elif corp_field.field_name == 'payment_method':
                                if corp_memb.payment_method:
                                    value = corp_memb.payment_method.human_name
                                
                        else:
                            value = getattr(corp_memb, corp_field.field_name)
                        
                    else:
                        if field_entries_d.has_key(corp_field.id):
                            value = field_entries_d[corp_field.id]
                        
                    if value == None:
                        value = ''
                    value_type = type(value)
                    if (value_type is bool) or (value_type is long) or (value_type is int):
                        value = str(value)
                    data_row.append(value.replace(',', ' '))
                
                for field in extra_field_names:
                    value = ''
                    if field == 'dues_reps':
                        dues_reps = CorporateMembershipRep.objects.filter(corporate_membership=corp_memb,
                                                                        is_dues_rep=True)
                        if dues_reps:
                            value = '; '.join(['%s (%s)' % (dues_rep.user.get_full_name(), dues_rep.user.username) for dues_rep in dues_reps])
                    elif field == 'invoice_id':
                        if corp_memb.invoice:
                            invoice_id = corp_memb.invoice.id
                            value = invoice_id
                    elif field == 'total':
                        if corp_memb.invoice:
                            total = corp_memb.invoice.total
                            value = "$%s" % total
                    elif field == 'balance':
                        if corp_memb.invoice:
                            balance = corp_memb.invoice.balance
                            value = "$%s" % balance
                    else:
                        value = getattr(corp_memb, field)
                        if field == 'expiration_dt' and (not corp_memb.expiration_dt):
                            value = 'never expire'
                    value_type = type(value)
                    if (value_type is bool) or (value_type is long) or (value_type is int):
                        value = str(value)
                    data_row.append(value)
                                        
                data_row.append('\n')
                data_row_list.append(data_row)
            EventLog.objects.log()

            return render_excel(filename, label_list, data_row_list, '.csv')
                    
    return render_to_response(template_name, {
            'form':form
            }, context_instance=RequestContext(request))

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
