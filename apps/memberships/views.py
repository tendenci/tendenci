from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
from event_logs.models import EventLog
from memberships.models import App, AppEntry
from memberships.forms import AppForm, AppEntryForm
from perms.models import ObjectPermission
from datetime import datetime, timedelta
import hashlib
from django.contrib.auth.models import User
from memberships.models import Membership
import sys
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from perms.utils import is_admin
from base.http import Http403

try:
    from notification import models as notification
except:
    notification = None

@login_required
def application_details(request, slug=None, template_name="memberships/applications/details.html"):
    """
    Display a built membership application and handle submission.
    """
    if not is_admin(request.user):
        raise Http403

    if not slug:
        raise Http404

    query = '"slug:%s"' % slug
    sqs = App.objects.search(query, user=request.user)

    if sqs:
        app = sqs[0].object
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

    app_entry_form = AppEntryForm(app, request.POST or None, request.FILES or None)
    if request.method == "POST":
        if app_entry_form.is_valid():
            app_entry = app_entry_form.save()

            membership_type = app_entry.membership_type

            if membership_type and not membership_type.require_approval:
                # create user and create membership

                user_dict = {
                    'username': app_entry.email,
                    'email': app_entry.email,
                    'password': hashlib.sha1(app_entry.email).hexdigest()[:6],
                }

                try:
                    user = User.objects.create_user(**user_dict)
                except:
                    user = None

                if user:
                    membership_dict = {
                        'member_number': app_entry.app.entries.count(),
                        'membership_type':membership_type,
                        'user':user,
                        'renewal':membership_type.renewal,
                        'join_dt':datetime.now(),
                        'renew_dt':datetime.now() + timedelta(30), # TODO: calculate renew_dt
                        'expiration_dt': membership_type.get_expiration_dt(join_dt = datetime.now()),
                        'approved': True,
                        'approved_denied_dt': datetime.now(),
                        'approved_denied_user': None,
                        'corporate_membership': None,
                        'payment_method':'',
                        'ma':app_entry.app,
                        'creator':user,
                        'creator_username':user.username,
                        'owner':user,
                        'owner_username':user,
                    }

                    membership = Membership.objects.create(**membership_dict)

            return redirect(app_entry.confirmation_url)

    return render_to_response(template_name, {
        'app': app, "app_entry_form": app_entry_form}, 
        context_instance=RequestContext(request))

def application_confirmation(request, hash=None, template_name="memberships/applications/confirmation.html"):
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

    # TODO: log this event; we do not have an id for this action

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

    query = '"id:%s"' % id
    sqs = AppEntry.objects.search(query, user=request.user)

    if sqs:
        entry = sqs[0].object
    else:
        raise Http404

    # TODO: log this event; we do not have an id for this action

    return render_to_response(template_name, {'entry': entry},
        context_instance=RequestContext(request))

@login_required
def application_entries_search(request, template_name="memberships/entries/search.html"):
    """
    Displays a page for searching membership application entries.
    """
    if not is_admin(request.user):
        raise Http403

    query = request.GET.get('q', None)
    entries = AppEntry.objects.search(query, user=request.user)
    entries = entries.order_by('entry_time')

    # TODO: log this event; we do not have an id for this action

    return render_to_response(template_name, {'entries':entries},
        context_instance=RequestContext(request))

@login_required
def approve_entry(request, id=None, template_name="memberships/entries/search.html"):
    """
    Approve membership application entry; then redirect at your discretion
    """

    if not is_admin(request.user):
        raise Http403

    if not id:
        raise Http404

    app_entry = AppEntry.objects.get(pk=id)

    user_dict = {
        'username': app_entry.email,
        'email': app_entry.email,
        'password': hashlib.sha1(app_entry.email).hexdigest()[:6],
    }

    try:
        user = User.objects.get(email=user_dict['email'])
        if not user:
            user = User.objects.create_user(**user_dict)
    except:
        print sys.exc_info()[1]
        user = None

    if user:
        membership_dict = {
            'member_number': app_entry.app.entries.count(),
            'membership_type': app_entry.membership_type,
            'user':user,
            'renewal': app_entry.membership_type.renewal,
            'join_dt':datetime.now(),
            'renew_dt':datetime.now() + timedelta(30), # TODO: calculate renew_dt
            'expiration_dt': datetime.now() + timedelta(365), # TODO: calculate expiration_dt
            'approved': True,
            'approved_denied_dt': datetime.now(),
            'approved_denied_user': request.user,
            'corporate_membership': None,
            'payment_method':'',
            'ma':app_entry.app,
            'creator':user,
            'creator_username':user.username,
            'owner':user,
            'owner_username':user,
        }

        membership = Membership.objects.create(**membership_dict)

    app_entry.membership = membership
    app_entry.save()

    # TODO: log this event; we do not have an id for this action
    return redirect(reverse('membership.application_entries', args=[app_entry.pk]))
    return render_to_response(template_name, {}, context_instance=RequestContext(request))