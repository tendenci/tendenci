import hashlib
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType, ContentTypeManager
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from event_logs.models import EventLog
from memberships.models import App, AppEntry, Notice
from perms.models import ObjectPermission
from base.http import Http403

from memberships.models import Membership, MembershipType, Notice
from memberships.forms import AppForm, AppEntryForm, AppCorpPreForm, MemberApproveForm, CSVForm, ReportForm
from memberships.utils import new_mems_from_csv

from user_groups.models import GroupMembership
from perms.utils import get_notice_recipients, \
    has_perm, update_perms_and_save, is_admin, is_member, is_developer

from invoices.models import Invoice
from corporate_memberships.models import CorporateMembership

from geraldo.generators import PDFGenerator
from reports import ReportNewMems

from datetime import datetime, timedelta

try:
    from notification import models as notification
except:
    notification = None

def membership_index(request):
    return HttpResponseRedirect(reverse('membership.search'))

def membership_search(request, template_name="memberships/search.html"):
    query = request.GET.get('q', None)
    members = Membership.objects.search(query, user=request.user)
    types = MembershipType.objects.all()

    return render_to_response(template_name, {'members': members, 'types': types},
        context_instance=RequestContext(request))    


@login_required
def membership_details(request, id=0, template_name="memberships/details.html"):
    """
    Membership details.
    """
    query = 'pk:%s' % id
    sqs = Membership.objects.search(query, user=request.user)

    if sqs:
        membership = sqs.best_match().object
    else:
        raise Http404

    # log membership details view
    EventLog.objects.log(**{
        'event_id' : 475000,
        'event_data': '%s (%d) viewed by %s' % (membership._meta.object_name, membership.pk, request.user),
        'description': '%s viewed' % membership._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': membership,
    })

    return render_to_response(template_name, {'membership': membership},
        context_instance=RequestContext(request))


def application_details(request, slug=None, cmb_id=None, membership_id=0, template_name="memberships/applications/details.html"):
    """
    Display a built membership application and handle submission.
    """
    if not slug:
        raise Http404

    query = '"slug:%s"' % slug
    apps = App.objects.search(query, user=request.user)

    if apps:
        app = apps.best_match().object
    else:
        raise Http404
    
    # if this app is for corporation individuals, redirect them to corp-pre page first.
    # from there, we can decide which corp they'll be in.
    is_corp_ind = False
    if hasattr(app, 'corp_app') and app.corp_app:
        is_corp_ind = True

        if request.method != "POST":
            http_referer = request.META.get('HTTP_REFERER', '')
            corp_pre_url = reverse('membership.application_details_corp_pre', args=[slug])
            if not http_referer or not corp_pre_url in http_referer:
                return redirect(corp_pre_url)

    # log application details view
    EventLog.objects.log(**{
        'event_id' : 655000,
        'event_data': '%s (%d) viewed by %s' % (app._meta.object_name, app.pk, request.user),
        'description': '%s viewed' % app._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': app,
    })

    if is_corp_ind and cmb_id:
        corporate_membership = CorporateMembership.objects.get(id=cmb_id)
    else:
        corporate_membership = None

    user = request.user
    membership = user.memberships.get_membership()
    user_member_requirements = [
        is_developer(request.user) == False,
        is_admin(request.user) == False,
        is_member(request.user) == True,
    ]

    initial_dict = {}

    # deny access to renew memberships
    if all(user_member_requirements):
        initial_dict = membership.get_app_initial()
        if not membership.can_renew():
            return render_to_response("memberships/applications/no-renew.html", {
                "app": app, "user":user, "membership": membership}, 
                context_instance=RequestContext(request))

    app_entry_form = AppEntryForm(
            app, 
            request.POST or None, 
            request.FILES or None, 
            user=request.user, 
            corporate_membership=corporate_membership,
            initial=initial_dict,
        )

    if request.method == "POST":
        if app_entry_form.is_valid():

            entry = app_entry_form.save(commit=False)
            entry_invoice = entry.save_invoice()

            # bind to user; assert renewal
            if request.user.is_authenticated():
                entry.user = request.user
                if all(user_member_requirements):
                    entry.is_renewal = True

                entry.save()

            # administrators go to approve/disapprove page
            if is_admin(request.user):
                return redirect(reverse('membership.application_entries', args=[entry.pk]))

            # online payment
            if entry.payment_method.is_online:
                return HttpResponseRedirect(reverse(
                    'payments.views.pay_online',
                    args=[entry_invoice.pk, entry_invoice.guid]
                ))

            if not entry.membership_type.require_approval:

                    entry.approve()

                    membership_total = Membership.objects.filter(status=True, status_detail='active').count()

                    notice_dict = {
                        'notice_time':'attimeof',
                        'notice_type':'join',
                        'status':True,
                        'status_detail':'active',
                    }

                    if entry.is_renewal:
                        notice_dict['notice_type'] = 'renewal'

                    # send email to member
                    for notice in Notice.objects.filter(**notice_dict):

                        notice_requirements = [
                           notice.membership_type == entry.membership_type,
                           notice.membership_type == None, 
                        ]

                        if any(notice_requirements):
                            notification.send_emails([entry.email],'membership_approved_to_member', {
                                'subject': notice.get_subject(entry.membership),
                                'content': notice.get_content(entry.membership),
                            })

                    # send email to admins
                    recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
                    if recipients and notification:
                        notification.send_emails(recipients,'membership_approved_to_admin', {
                            'object':entry,
                            'request':request,
                            'membership_total':membership_total,
                        })

                    # log - entry approval
                    EventLog.objects.log(**{
                        'event_id' : 1082101,
                        'event_data': '%s (%d) approved by %s' % (entry._meta.object_name, entry.pk, entry.judge),
                        'description': '%s viewed' % entry._meta.object_name,
                        'user': request.user,
                        'request': request,
                        'instance': entry,
                    })

            # log - entry submission
            EventLog.objects.log(**{
                'event_id' : 1081000,
                'event_data': '%s (%d) submitted by %s' % (entry._meta.object_name, entry.pk, request.user),
                'description': '%s viewed' % entry._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': entry,
            })

            return redirect(entry.confirmation_url)

    return render_to_response(template_name, {
        'app': app, "app_entry_form": app_entry_form}, 
        context_instance=RequestContext(request))
    
def application_details_corp_pre(request, slug, cmb_id=None, template_name="memberships/applications/details_corp_pre.html"):

    try:
        app = App.objects.get(slug=slug)
    except App.DoesNotExist:
        raise Http404

    if not hasattr(app, 'corp_app'):
        raise Http404
    
    if not app.corp_app:
        raise Http404
        
    
    form = AppCorpPreForm(request.POST or None)
    if is_admin(request.user) or app.corp_app.authentication_method == 'admin':
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
    else: # secret_code
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
            
            return redirect(reverse('membership.application_details', args=[app.slug, corporate_membership_id]))
    
    
    return render_to_response(template_name, {
        'app': app, "form": form}, 
        context_instance=RequestContext(request))

def application_confirmation(request, hash=None, template_name="memberships/entries/details.html"):
    """
    Display this confirmation have a membership application is submitted.
    """

    if not hash:
        raise Http404

    query = '"hash:%s"' % hash
    sqs = AppEntry.objects.search(query, user=request.user)

    if sqs:
        entry = sqs[0].object
    else:
        raise Http404

    return render_to_response(template_name, {'entry': entry},
        context_instance=RequestContext(request))

@login_required
def application_entries(request, id=None, template_name="memberships/entries/details.html"):
    """
    Displays the details of a membership application entry.
    """

    if not is_admin(request.user):
        raise Http403

    if not id:
        return HttpResponseRedirect(reverse('membership.application_entries_search'))


    # TODO: Not use search but query the database
    # TODO: Needs a manager to query database with permission checks
    query = '"id:%s"' % id
    sqs = AppEntry.objects.search(query, user=request.user)

    if sqs:
        entry = sqs[0].object
    else:
        raise Http404

    # log entry view
    EventLog.objects.log(**{
        'event_id' : 1085000,
        'event_data': '%s (%d) viewed by %s' % (entry._meta.object_name, entry.pk, request.user),
        'description': '%s viewed' % entry._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': entry,
    })

    if request.method == "POST":
        form = MemberApproveForm(entry, request.POST)
        if form.is_valid():

            membership_total = Membership.objects.filter(status=True, status_detail='active').count()

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

                entry.approve()

                notice_dict = {
                    'notice_time':'attimeof',
                    'notice_type':'join',
                    'status':True,
                    'status_detail':'active',
                }

                if entry.is_renewal:
                    notice_dict['notice_type'] = 'renewal'

                # send email to member
                for notice in Notice.objects.filter(**notice_dict):

                    notice_requirements = [
                       notice.membership_type == entry.membership_type,
                       notice.membership_type == None, 
                    ]

                    if any(notice_requirements):
                        notification.send_emails([entry.email],'membership_approved_to_member', {
                            'subject': notice.get_subject(entry.membership),
                            'content': notice.get_content(entry.membership),
                        })

                # send email to admins
                recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
                if recipients and notification:
                    notification.send_emails(recipients,'membership_approved_to_admin', {
                        'object':entry,
                        'request':request,
                        'membership_total':membership_total,
                    })

                # log entry approved
                EventLog.objects.log(**{
                    'event_id' : 1085000,
                    'event_data': '%s (%d) approved by %s' % (entry._meta.object_name, entry.pk, request.user),
                    'description': '%s approved' % entry._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': entry,
                })

            else:
                entry.disapprove()

                # send email to disapproved membership applicant
                notification.send_emails([entry.email],'membership_disapproved_to_member', {
                    'object':entry,
                    'request':request,
                    'membership_total':membership_total,
                })

                # send email to admins
                recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
                if recipients and notification:
                    notification.send_emails(recipients,'membership_disapproved_to_admin', {
                        'object': entry,
                        'request': request,
                        'membership_total': membership_total,
                    })

                # log entry disapproved
                EventLog.objects.log(**{
                    'event_id' : 1082102,
                    'event_data': '%s (%d) disapproved by %s' % (entry._meta.object_name, entry.pk, request.user),
                    'description': '%s disapproved' % entry._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': entry,
                })

            return redirect(reverse('membership.application_entries', args=[entry.pk]))

    else:
        form = MemberApproveForm(entry)

    return render_to_response(template_name, {
        'entry': entry,
        'form': form,
        }, context_instance=RequestContext(request))

@login_required
def application_entries_search(request, template_name="memberships/entries/search.html"):
    """
    Displays a page for searching membership application entries.
    """

    if not is_admin(request.user):
        raise Http403

    query = request.GET.get('q', None)
    entries = AppEntry.objects.search(query, user=request.user)
    entries = entries.order_by('-entry_time')

    apps = App.objects.all()
    types = MembershipType.objects.all()

    # log entry search view
    EventLog.objects.log(**{
        'event_id' : 1084000,
        'event_data': '%s searched by %s' % ('Membership Entries', request.user),
        'description': '%s searched' % 'Membership Entries',
        'user': request.user,
        'request': request,
        #'instance': app,
    })

    return render_to_response(template_name, {
        'entries':entries,
        'apps':apps,
        'types':types,
        }, context_instance=RequestContext(request))
    
@login_required    
def notice_email_content(request, id, template_name="memberships/notices/email_content.html"):
    if not is_admin(request.user):
        raise Http403
    notice = get_object_or_404(Notice, pk=id)
    
    return render_to_response(template_name, {
        'notice':notice,
        }, context_instance=RequestContext(request))

@login_required
def import_membership_csv(request, template_name="memberships/csv_form.html"):
    """
    Displays a page for uploading a tendenci4 CSV file
    """
    
    if not is_admin(request.user):
        raise Http403
    
    if request.method == 'POST':
        form = CSVForm(request.POST, request.FILES)
        if form.is_valid():
            new_mems_from_csv(request.FILES['csv'], form.cleaned_data['app'], request.user.id)
            return redirect(import_membership_csv)
    else:
        form = CSVForm()
    
    return render_to_response(template_name, {
        'form':form,
        }, context_instance=RequestContext(request))


#REPORTS
    
def _membership_joins(from_date):
    return Membership.objects.filter(join_dt__gte=from_date)

@staff_member_required
def membership_join_report(request):
    now = datetime.now()
    mems = Membership.objects.all()
    mem_type = ''
    mem_stat = ''
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['membership_type']:
                mem_type = form.cleaned_data['membership_type']
                mems = mems.filter(membership_type = form.cleaned_data['membership_type'])
            if form.cleaned_data['membership_status']:
                mem_stat = form.cleaned_data['membership_status']
                if form.cleaned_data['membership_status'] == 'ACTIVE':
                    mems = mems.filter(expiration_dt__gte = now, join_dt__lte = now)
                else:
                    mems = mems.exclude(expiration_dt__gte = now, join_dt__lte = now)
    else:
        form = ReportForm()
    mems30days = mems.filter(join_dt__gte = now-timedelta(days=30))
    mems60days = mems.filter(join_dt__gte = now-timedelta(days=60))
    mems90days = mems.filter(join_dt__gte = now-timedelta(days=90))
    return render_to_response(
                'reports/membership_joins.html', {
                    'mems30days': mems30days,
                    'mems60days': mems60days,
                    'mems90days': mems90days,
                    'form': form,
                    'mem_type': mem_type,
                    'mem_stat': mem_stat,
                },
                context_instance=RequestContext(request))

@staff_member_required
def membership_join_report_pdf(request):
    now = datetime.now()
    days = request.GET.get('days', 30)
    mem_type = request.GET.get('mem_type', None)
    mem_stat = request.GET.get('mem_stat', None)
    mems = Membership.objects.all()
    if mem_type:
        mems = mems.filter(membership_type=mem_type)
    if mem_stat:
        if mem_stat == 'ACTIVE':
            mems = mems.filter(expiration_dt__gte = now, join_dt__lte = now)
        else:
            mems = mems.exclude(expiration_dt__gte = now, join_dt__lte = now)
    mems = mems.filter(join_dt__gte = now-timedelta(days=int(days)))
    report = ReportNewMems(queryset = mems)
    resp = HttpResponse(mimetype='application/pdf')
    report.generate_by(PDFGenerator, filename=resp)
    return resp
