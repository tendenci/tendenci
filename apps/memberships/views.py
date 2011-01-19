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

    app_entry_form = AppEntryForm(app, request.POST or None, request.FILES or None)
    if request.method == "POST":
        if app_entry_form.is_valid():
            app_entry = app_entry_form.save(commit=False)

            app_entry.user = request.user
            app_entry.save()

            membership_type = app_entry.membership_type

            if app_entry.membership_type.require_approval:
            # create user and create membership

                spawned_username = '%s %s' % (app_entry.first_name, app_entry.last_name)
                spawned_username = re.sub('\s+', '_', spawned_username)
                spawned_username = re.sub('[^\w.-]+', '', spawned_username)
                spawned_username = spawned_username.strip('_.- ').lower()

                user_dict = {
                    'username': spawned_username,
                    'email': app_entry.email,
                    'password': hashlib.sha1(app_entry.email).hexdigest()[:6],
                }

                try:
                    user = User.objects.create_user(**user_dict)

                    user.first_name = app_entry.first_name
                    user.last_name = app_entry.last_name
                    user.save()

                except:
                    user = None

                if user:
                    membership_dict = {
                        'member_number': app_entry.app.entries.count(),
                        'membership_type':membership_type,
                        'user':user,
                        'renewal':membership_type.renewal,
                        'join_dt':datetime.now(),
                        'renew_dt': None,
                        'expiration_dt': membership_type.get_expiration_dt(join_dt = datetime.now()),
                        'approved': True,
                        'approved_denied_dt': datetime.now(),
                        'approved_denied_user': None,
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

            status = request.POST.get('status', '')
            approve = (status.lower() == 'approve')

            if approve:

                user = User.objects.get(pk=form.cleaned_data['users'])

                try: # get membership
                    membership = Membership.objects.get(ma=entry.app)
                except: # or create membership
                    membership = Membership.objects.create(**{
                        'member_number': entry.app.entries.count(),
                        'membership_type': entry.membership_type,
                        'user':user,
                        'renewal': entry.membership_type.renewal,
                        'join_dt':datetime.now(),
                        'renew_dt': None,
                        'expiration_dt': entry.membership_type.get_expiration_dt(join_dt=datetime.now()),
                        'approved': True,
                        'approved_denied_dt': datetime.now(),
                        'approved_denied_user': request.user,
                        'payment_method':'',
                        'ma':entry.app,
                        'creator':user,
                        'creator_username':user.username,
                        'owner':user,
                        'owner_username':user.username,
                    })

                # create group-membership object
                # this adds the user to the group
                    GroupMembership(**{
                    'group':entry.membership_type.group,
                    'member':user,
                    'creator_id': request.user.pk,
                    'creator_username':request.user.username,
                    'owner_id':request.user.pk,
                    'owner_username':request.user.username,
                    'status':True,
                    'status_detail':'active',
                })

                # mark as approved
                entry.is_approved = True
                entry.decision_dt = datetime.now()
                entry.judge = request.user

                entry.membership = membership
                entry.save()

            else:

                # mark as disapproved
                entry.is_approved = False
                entry.decision_dt = datetime.now()
                entry.judge = request.user

                entry.save()

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

@login_required
def approve_entry(request, id=0):
    """
    Approve membership application entry; then redirect at your discretion
    """
    # TODO: log event; eventid does not exist yet

    if not is_admin(request.user):
        raise Http403

    entry = get_object_or_404(AppEntry, pk=id)

    user_dict = {
        'username': entry.email,
        'email': entry.email,
        'password': hashlib.sha1(entry.email).hexdigest()[:6],
    }

    try: # get user
        user = User.objects.get(username=user_dict['username'])
    except: # or create user
        user = User.objects.create_user(**user_dict)

    try: # get membership
        membership = Membership.objects.get(ma=entry.app)
    except: # or create membership
        membership = Membership.objects.create(**{
            'member_number': entry.app.entries.count(),
            'membership_type': entry.membership_type,
            'user':user,
            'renewal': entry.membership_type.renewal,
            'join_dt':datetime.now(),
            'renew_dt': None,
            'expiration_dt': entry.membership_type.get_expiration_dt(join_dt=datetime.now()),
            'approved': True,
            'approved_denied_dt': datetime.now(),
            'approved_denied_user': request.user,
            'payment_method':'',
            'ma':entry.app,
            'creator':user,
            'creator_username':user.username,
            'owner':user,
            'owner_username':user.username,
        })

    # mark as approved
    entry.is_approved = True
    entry.decision_dt = datetime.now()
    entry.judge = request.user

    entry.membership = membership
    entry.save()

    return redirect(reverse('membership.application_entries', args=[entry.pk]))

@login_required
def disapprove_entry(request, id=0):
    """
        Mark application as disapproved.
        Travel to [disapproved] membership application page.
    """
    # TODO: log event; eventid does not exist yet

    query = 'id:%s' % id
    sqs = AppEntry.objects.search(query, user=request.user)

    if sqs:
        entry = sqs.best_match().object
    else:
        # assume 404; could have been 403
        raise Http404

    # mark as disapproved
    entry.is_approved = False
    entry.decision_dt = datetime.now()
    entry.judge = request.user

    entry.save()

    # redirect to application entry
    return redirect(reverse('membership.application_entries', args=[entry.pk]))
















    