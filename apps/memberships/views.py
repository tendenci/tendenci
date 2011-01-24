import re
import hashlib
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
from event_logs.models import EventLog
from memberships.models import App, AppEntry
from memberships.forms import AppForm, AppEntryForm
from perms.models import ObjectPermission
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from perms.utils import is_admin
from base.http import Http403
from memberships.models import Membership, MembershipType
from memberships.forms import MemberApproveForm
from user_groups.models import GroupMembership
from perms.utils import get_notice_recipients, has_perm

try:
    from notification import models as notification
except:
    notification = None

@login_required
def membership_details(request, id=0, template_name="memberships/details.html"):
    """
    Membership details.
    """
    # TODO: log this event; we do not have an id for this action

    query = 'pk:%s' % id
    sqs = Membership.objects.search(query, user=request.user)

    if sqs:
        membership = sqs.best_match().object
    else:
        raise Http404

    return render_to_response(template_name, {'membership': membership},
        context_instance=RequestContext(request))

def application_details(request, slug=None, template_name="memberships/applications/details.html"):
    """
    Display a built membership application and handle submission.
    """
    if not slug:
        raise Http404

    query = '"slug:%s"' % slug
    sqs = App.objects.search(query, user=request.user)

    if sqs:
        app = sqs.best_match().object
    else:
        raise Http404

    EventLog.objects.log(**{
        'event_id' : 655000,
        'event_data': '%s (%d) viewed by %s' % (app._meta.object_name, app.pk, request.user),
        'description': '%s viewed' % app._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': app,
    })

    app_entry_form = AppEntryForm(app, request.POST or None, request.FILES or None, user=request.user)
    if request.method == "POST":
        if app_entry_form.is_valid():

            membership_total = Membership.objects.filter(status=True, status_detail='active').count()

            entry = app_entry_form.save(commit=False)

            if request.user.is_authenticated():
                entry.user = request.user
                entry.save()

            if is_admin(request.user):
                return redirect(reverse('membership.application_entries', args=[entry.pk]))

            if not entry.membership_type.require_approval:

                    entry.approve()

                    # send email to approved membership applicant
                    notification.send_emails([entry.email],'membership_approved_to_member', {
                        'object':entry,
                        'request':request,
                        'membership_total':membership_total,
                    })

                    # send email to admins
                    recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
                    if recipients and notification:
                        notification.send_emails(recipients,'membership_approved_to_admin', {
                            'object':entry,
                            'request':request,
                            'membership_total':membership_total,
                        })

            return redirect(entry.confirmation_url)

    return render_to_response(template_name, {
        'app': app, "app_entry_form": app_entry_form}, 
        context_instance=RequestContext(request))

def application_confirmation(request, hash=None, template_name="memberships/entries/details.html"):
    """
    Display this confirmation have a membership application is submitted.
    """
    # TODO: log this event; we do not have an id for this action

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
    # TODO: log this event; we do not have an id for this action

    if not is_admin(request.user):
        raise Http403

    if not id:
        return HttpResponseRedirect(reverse('membership.application_entries_search'))

    query = '"id:%s"' % id
    sqs = AppEntry.objects.search(query, user=request.user)

    if sqs:
        entry = sqs[0].object
    else:
        raise Http404

    if request.method == "POST":
        form = MemberApproveForm(entry, request.POST)
        if form.is_valid():

            membership_total = Membership.objects.filter(status=True, status_detail='active').count()

            status = request.POST.get('status', '')
            approve = (status.lower() == 'approve')

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

                # send email to approved membership applicant
                notification.send_emails([entry.email],'membership_approved_to_member', {
                    'object':entry,
                    'request':request,
                    'membership_total':membership_total,
                })

                # send email to admins
                recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
                if recipients and notification:
                    notification.send_emails(recipients,'membership_approved_to_admin', {
                        'object':entry,
                        'request':request,
                        'membership_total':membership_total,
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
    # TODO: log this event; we do not have an id for this action

    if not is_admin(request.user):
        raise Http403

    query = request.GET.get('q', None)
    entries = AppEntry.objects.search(query, user=request.user)
    entries = entries.order_by('-entry_time')

    apps = App.objects.all()
    types = MembershipType.objects.all()

    return render_to_response(template_name, {
        'entries':entries,
        'apps':apps,
        'types':types,
        }, context_instance=RequestContext(request))