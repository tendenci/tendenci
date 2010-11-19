from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import Http404
from event_logs.models import EventLog
from memberships.models import App, AppEntry
from memberships.forms import AppForm, AppEntryForm
from perms.models import ObjectPermission
from datetime import datetime, timedelta
import hashlib
from django.contrib.auth.models import User
from memberships.models import Membership
import sys

try:
    from notification import models as notification
except:
    notification = None

def application_details(request, slug=None, template_name="memberships/applications/details.html"):
    """
    Display a built membership application and handle submission.
    """
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
                    print "err", sys.exc_info()[1]
                    print "user_dict", user_dict
                    user = None

                if user:
                    membership_dict = {
                        'member_number': app_entry.app.entries.count(),
                        'membership_type':membership_type,
                        'user':user,
                        'renewal':membership_type.renewal,
                        'join_dt':datetime.now(),
                        'renew_dt':datetime.now() + timedelta(30), # TODO: calculate renew_dt
                        'expiration_dt': datetime.now() + timedelta(365), # TODO: calculate expiration_dt
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
        app_entry = sqs[0].object
    else:
        raise Http404

    # TODO: log this event

    return render_to_response(template_name, {'app_entry': app_entry}, 
        context_instance=RequestContext(request))






