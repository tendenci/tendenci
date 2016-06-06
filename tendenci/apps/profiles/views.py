# django
import os
import math
import time
import subprocess
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.db.models import Count, Q, get_app
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
# for password change
from django.views.decorators.csrf import csrf_protect
import simplejson

from tendenci.apps.base.decorators import ssl_required, password_required
from tendenci.apps.base.utils import get_pagination_page_range

from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.perms.utils import (has_perm, update_perms_and_save,
                                       get_notice_recipients,
                                       get_query_filters
                                       )
from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.exports.utils import render_csv

# for group memberships
from tendenci.apps.user_groups.models import GroupMembership, Group
from tendenci.apps.user_groups.forms import GroupMembershipEditForm

from tendenci.apps.profiles.models import Profile, UserImport, UserImportData
from tendenci.apps.profiles.forms import (ProfileForm, ExportForm,
UserPermissionForm, UserGroupsForm, ValidatingPasswordChangeForm,
UserMembershipForm, ProfileMergeForm, ProfileSearchForm, UserUploadForm,
ActivateForm)
from tendenci.apps.profiles.utils import get_member_reminders, ImportUsers
from tendenci.apps.events.models import Registrant
from tendenci.apps.memberships.models import MembershipType
from tendenci.apps.invoices.models import Invoice

try:
    notification = get_app('notifications')
except ImproperlyConfigured:
    notification = None

friends = False


@login_required
def index(request, username='', template_name="profiles/index.html"):
    """
    Show profile of username passed.  If no username is passed
    then redirect to username of person logged in.
    """

    if not username:
        return HttpResponseRedirect(reverse('profile', args=[request.user.username]))

    user_this = get_object_or_404(User, username=username)

    try:
        profile = user_this.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create_profile(user=user_this)

    if not profile.allow_view_by(request.user):
        raise Http403

    # content counts
    content_counts = {'total': 0, 'invoice': 0}

    inv_count = Invoice.objects.filter(Q(owner=user_this) |
                                        Q(bill_to_email=user_this.email)).count()
    content_counts['invoice'] = inv_count
    content_counts['total'] += inv_count

    # owners
    additional_owner_ids = ObjectPermission.objects.users_with_perms('profiles.change_profile', profile)
    additional_owners = []
    for id in additional_owner_ids:
        try:
            tmp_user = User.objects.get(pk=id)
            additional_owners.append(tmp_user)
        except User.DoesNotExist:
            pass
    if additional_owners:
        if profile.owner in additional_owners:
            additional_owners.remove(profile.owner)

    # group list
    group_memberships = user_this.group_member.filter(group__status=True)

    active_qs = Q(status_detail__iexact='active')
    pending_qs = Q(status_detail__iexact='pending')
    expired_qs = Q(status_detail__iexact='expired')

    if request.user == user_this or request.user.profile.is_superuser:
        memberships = user_this.membershipdefault_set.filter(
            status=True) & user_this.membershipdefault_set.filter(
                active_qs | pending_qs | expired_qs)
    else:
        memberships = user_this.membershipdefault_set.filter(
            status=True) & user_this.membershipdefault_set.filter(
                active_qs | expired_qs)

    registrations = Registrant.objects.filter(user=user_this)

    EventLog.objects.log(instance=profile)

    state_zip = ' '.join([s for s in (profile.state, profile.zipcode) if s])
    city_state = ', '.join([s for s in (profile.city, profile.state) if s])
    city_state_zip = ', '.join([s for s in (profile.city, state_zip, profile.country) if s])

    can_edit = has_perm(request.user, 'profiles.change_profile', user_this)

    if not can_edit:
        can_edit = request.user == user_this

    multiple_apps = False
    if get_setting('module', 'memberships', 'enabled'):
        from tendenci.apps.memberships.models import MembershipApp
        membership_apps = MembershipApp.objects.filter(
                               status=True,
                               status_detail__in=['published',
                                                  'active']
                                ).values('id', 'name', 'slug'
                                         ).order_by('name')
        if len(membership_apps) > 1:
            multiple_apps = True
    else:
        membership_apps = None

    membership_reminders = ()
    if request.user == user_this:
        membership_reminders = get_member_reminders(user_this)

    return render_to_response(template_name, {
        'can_edit': can_edit,
        "user_this": user_this,
        "profile": profile,
        'city_state': city_state,
        'city_state_zip': city_state_zip,
        'content_counts': content_counts,
        'additional_owners': additional_owners,
        'group_memberships': group_memberships,
        'memberships': memberships,
        'registrations': registrations,
        'membership_apps': membership_apps,
        'multiple_apps': multiple_apps,
        'membership_reminders': membership_reminders,
        }, context_instance=RequestContext(request))


def search(request, template_name="profiles/search.html"):
    # check if allow anonymous user search
    allow_anonymous_search = get_setting('module', 'users', 'allowanonymoususersearchuser')
    allow_user_search = get_setting('module', 'users', 'allowusersearch')
    membership_view_perms = get_setting('module', 'memberships', 'memberprotection')

    if not request.user.profile.is_superuser:
        # block anon
        if request.user.is_anonymous():
            if not allow_anonymous_search:
                raise Http403
            if not allow_user_search:
                raise Http403

        # block member or user
        if request.user.is_authenticated():
            if request.user.profile.is_member:  # if member
                if membership_view_perms == 'private':
                    if not allow_user_search:
                        raise Http403
            else:  # if just user
                if not allow_user_search:
                    raise Http403

    # decide whether or not to display the membership types drop down
    display_membership_type = False
    if membership_view_perms == 'public' or request.user.profile.is_superuser:
        display_membership_type = True
    else:
        if membership_view_perms in ['all-members', 'member-type']:
            if request.user.is_authenticated() and \
                request.user.profile.is_member:
                display_membership_type = True
    mt_ids_list = None
    if display_membership_type:
        if membership_view_perms == 'member-type':
            mt_ids_list = request.user.membershipdefault_set.filter(
                                            status=True,
                                               status_detail='active'
                                               ).values_list(
                                            'membership_type_id',
                                            flat=True)
            if mt_ids_list:
                mts = MembershipType.objects.filter(id__in=mt_ids_list
                                                    ).order_by('name')
            else:
                mts = None
        else:
            mts = MembershipType.objects.all().order_by('name')
    else:
        mts = None

    show_member_option = mts

    form = ProfileSearchForm(request.GET, mts=mts)
    if form.is_valid():
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        search_criteria = form.cleaned_data['search_criteria']
        search_text = form.cleaned_data['search_text']
        search_method = form.cleaned_data['search_method']
        membership_type = form.cleaned_data.get('membership_type', None)
        member_only = form.cleaned_data.get('member_only', False)
    else:
        first_name = None
        last_name = None
        email = None
        search_criteria = None
        search_text = None
        search_method = None
        membership_type = None
        member_only = False

    profiles = Profile.objects.filter(Q(status=True))
    if not request.user.profile.is_superuser:
        profiles = profiles.filter(Q(status_detail="active"))
        if request.user.is_authenticated() and request.user.profile.is_member:            
            filters = get_query_filters(request.user, 'profiles.view_profile')
        
            if membership_view_perms == 'private':
                # show non-members only
                profiles = profiles.filter(member_number='')  # exclude all members
            elif membership_view_perms == 'member-type':
                filters = Q(member_number='')
                if mt_ids_list:
                    filters = filters | Q(
                    user__membershipdefault__membership_type_id__in=mt_ids_list)
                profiles = profiles.filter(filters)

            elif membership_view_perms == 'all-members':
                from tendenci.apps.memberships.models import MembershipDefault
                filters = filters | Q(
                    user__id__in=MembershipDefault.objects.filter(status=True,
                                                                  status_detail='active'
                                                ).values_list('user_id'))
                profiles = profiles.filter(filters)
    
            if not allow_user_search:
                # exclude non-members
                profiles = profiles.exclude(member_number='')
    
        else: # non-member
            if membership_view_perms != 'public':
                # show non-members only
                profiles = profiles.filter(member_number='')           

    profiles = profiles.distinct()

    if first_name:
        profiles = profiles.filter(user__first_name__iexact=first_name)
    if last_name:
        profiles = profiles.filter(user__last_name__iexact=last_name)
    if email:
        profiles = profiles.filter(user__email__iexact=email)

    if member_only:
        profiles = profiles.exclude(member_number='')

    if search_criteria and search_text:
        search_type = '__iexact'
        if search_method == 'starts_with':
            search_type = '__istartswith'
        elif search_method == 'contains':
            search_type = '__icontains'
        if search_criteria in ['username', 'first_name', 'last_name', 'email']:
            search_filter = {'user__%s%s' % (search_criteria,
                                             search_type): search_text}
        else:
            search_filter = {'%s%s' % (search_criteria,
                                         search_type): search_text}

        profiles = profiles.filter(**search_filter)

    if not request.user.profile.is_superuser:
        if not has_perm(request.user, 'profiles.view_profile'):
            profiles = profiles.exclude(hide_in_search=True)

    if membership_type:
        profiles = profiles.filter(
            user__membershipdefault__membership_type_id=membership_type)

    profiles = profiles.order_by('user__last_name', 'user__first_name')

    EventLog.objects.log()
    return render_to_response(template_name, {
            'profiles': profiles,
            'user_this': None,
            'search_form': form,
            'show_member_option': show_member_option},
        context_instance=RequestContext(request))


@login_required
def add(request, form_class=ProfileForm, template_name="profiles/add.html"):
    if not has_perm(request.user,'profiles.add_profile'):raise Http403

    required_fields = get_setting('module', 'users', 'usersrequiredfields')
    if required_fields:
        required_fields_list = required_fields.split(',')
        required_fields_list = [field.strip() for field in required_fields_list]
    else:
        required_fields_list = None

    if request.method == "POST":
        form = form_class(request.POST,
                          user_current=request.user,
                          user_this=None,
                          required_fields_list=required_fields_list)

        if form.is_valid():
            profile = form.save(request, None)
            new_user = profile.user

            # security_level
            if request.user.profile.is_superuser:
                security_level = form.cleaned_data['security_level']
                if security_level == 'superuser':
                    new_user.is_superuser = 1
                    new_user.is_staff = 1
                elif security_level == 'staff':
                    new_user.is_superuser = 0
                    new_user.is_staff = 1

                else:
                    new_user.is_superuser = 0
                    new_user.is_staff = 0

                # set up user permission
                profile.allow_user_view, profile.allow_user_edit = False, False

            else:
                new_user.is_superuser = 0
                new_user.is_staff = 0

            # interactive
            interactive = form.cleaned_data['interactive']
            try:
                interactive = int(interactive)
            except:
                interactive = 0

            new_user.is_active = interactive

            profile.save()
            new_user.save()

            ObjectPermission.objects.assign(new_user, profile)

            # send notification to administrators
            recipients = get_notice_recipients('module', 'users', 'userrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': profile,
                        'request': request,
                    }
                    notification.send_emails(recipients,'user_added', extra_context)

            return HttpResponseRedirect(reverse('profile', args=[new_user.username]))
    else:
        form = form_class(user_current=request.user,
                          user_this=None,
                          required_fields_list=required_fields_list)
    auto_pwd = request.POST.get('auto_pwd')
    return render_to_response(template_name, {'form':form, 'user_this':None,
                                              'required_fields_list': required_fields_list,
                                              'auto_pwd': auto_pwd
                                              },
        context_instance=RequestContext(request))


@login_required
def edit(request, id, form_class=ProfileForm, template_name="profiles/edit.html"):
    user_edit = get_object_or_404(User, pk=id)

    try:
        profile = Profile.objects.get(user=user_edit)
    except Profile.DoesNotExist:
        profile = Profile.objects.create_profile(user=user_edit)
    if profile.language == 'en-us':
        profile.language = 'en'

    if not profile.allow_edit_by(request.user): raise Http403

    required_fields = get_setting('module', 'users', 'usersrequiredfields')
    if required_fields:
        required_fields_list = required_fields.split(',')
        required_fields_list = [field.strip() for field in required_fields_list]
    else:
        required_fields_list = None

    if request.method == "POST":
        form = form_class(request.POST,
                          user_current=request.user,
                          user_this=user_edit,
                          required_fields_list=required_fields_list,
                          instance=profile)

        if form.is_valid():
            # get the old profile, so we know what has been changed in admin notification
            old_user = User.objects.get(id=id)
            old_profile = Profile.objects.get(user=old_user)
            profile = form.save(request, user_edit)

            if request.user.profile.is_superuser:
                # superusers cannot demote themselves
                if user_edit == request.user:
                    security_level = 'superuser'
                    if form.cleaned_data['security_level'] != 'superuser':
                        messages.add_message(request, messages.INFO, _("You cannot convert yourself to \"%(role)s\" role.") % {'role' : form.cleaned_data['security_level']})
                else:
                    security_level = form.cleaned_data['security_level']

                if security_level == 'superuser':
                    user_edit.is_superuser = 1
                    user_edit.is_staff = 1
                    # remove them from auth_group if any - they don't need it
                    user_edit.groups = []
                elif security_level == 'staff':
                    user_edit.is_superuser = 0
                    user_edit.is_staff = 1
                else:
                    user_edit.is_superuser = 0
                    user_edit.is_staff = 0
                    # remove them from auth_group if any
                    user_edit.groups = []


                # set up user permission
                profile.allow_user_view, profile.allow_user_edit = False, False

            else:
                user_edit.is_superuser = 0
                user_edit.is_staff = 0

            # interactive
            interactive = form.cleaned_data['interactive']
            try:
                interactive = int(interactive)
            except:
                interactive = 0
            if interactive == 1:
                user_edit.is_active = 1
            else:
                user_edit.is_active = 0

            user_edit.save()
            profile.save()

            # update member-number on profile
            profile.refresh_member_number()

            # notify ADMIN of update to a user's record
            if get_setting('module', 'users', 'userseditnotifyadmin'):
            #    profile_edit_admin_notify(request, old_user, old_profile, profile)
                # send notification to administrators
                recipients = get_notice_recipients('module', 'users', 'userrecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'old_user': old_user,
                            'old_profile': old_profile,
                            'profile': profile,
                            'request': request,
                        }
                        notification.send_emails(recipients,'user_edited', extra_context)

            return HttpResponseRedirect(reverse('profile', args=[user_edit.username]))
    else:
        if profile:
            form = form_class(user_current=request.user,
                          user_this=user_edit,
                          required_fields_list=required_fields_list,
                          instance=profile)

        else:
            form = form_class(user_current=request.user,
                          user_this=user_edit,
                          required_fields_list=required_fields_list)

    return render_to_response(template_name, {'user_this':user_edit, 'profile':profile, 'form':form,
                                              'required_fields_list':required_fields_list},
        context_instance=RequestContext(request))




def delete(request, id, template_name="profiles/delete.html"):
    user = get_object_or_404(User, pk=id)
    try:
        profile = Profile.objects.get(user=user)
    except:
        profile = None

    if not has_perm(request.user,'profiles.delete_profile',profile): raise Http403

    if request.method == "POST":
        recipients = get_notice_recipients('module', 'users', 'userrecipients')
        if recipients:
            if notification:
                extra_context = {
                    'profile': profile,
                    'request': request,
                }
                notification.send_emails(recipients,'user_deleted', extra_context)
        #soft delete
        #profile.delete()
        #user.delete()
        if profile:
            profile.status_detail = 'inactive'
            profile.save()
        user.is_active = False
        user.save()


        return HttpResponseRedirect(reverse('profile.search'))

    return render_to_response(template_name, {'user_this':user, 'profile': profile},
        context_instance=RequestContext(request))


@login_required
def edit_user_perms(request, id, form_class=UserPermissionForm, template_name="profiles/edit_perms.html"):
    user_edit = get_object_or_404(User, pk=id)

    try:
        profile = Profile.objects.get(user=user_edit)
    except Profile.DoesNotExist:
        profile = Profile.objects.create_profile(user=user_edit)

    # for now, only admin can grant/remove permissions
    if not request.user.profile.is_superuser:
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST, request.user, instance=user_edit)
    else:
        form = form_class(instance=user_edit)
    if form.is_valid():
        user_edit.user_permissions = form.cleaned_data['user_permissions']
        user_edit.save()

        EventLog.objects.log(instance=profile)

        return HttpResponseRedirect(reverse('profile', args=[user_edit.username]))

    return render_to_response(template_name, {'user_this':user_edit, 'profile':profile, 'form':form},
        context_instance=RequestContext(request))


def _get_next(request):
    """
    The part that's the least straightforward about views in this module is how they
    determine their redirects after they have finished computation.

    In short, they will try and determine the next place to go in the following order:

    1. If there is a variable named ``next`` in the *POST* parameters, the view will
    redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, the view will
    redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, the view will
    redirect to that previous page.
    """
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    if not next:
        next = request.path
    return next


@ssl_required
@csrf_protect
@login_required
def password_change(request, id, template_name='registration/custom_password_change_form.html',
                    post_change_redirect=None, password_change_form=ValidatingPasswordChangeForm):
    user_edit = get_object_or_404(User, pk=id)
    if post_change_redirect is None:
        post_change_redirect = reverse('profile', kwargs={'username': user_edit.username})
    if request.method == "POST":
        form = password_change_form(user=user_edit, data=request.POST)
        if request.user.profile.is_superuser:
            del form.fields['old_password']
        if form.is_valid():
            form.save()
            messages.add_message(
                request, messages.SUCCESS, _("Successfully updated your password."))
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=user_edit)
        # an admin doesn't have to enter the old password
        if request.user.profile.is_superuser:
            del form.fields['old_password']
    return render_to_response(template_name, {
        'user_this': user_edit,
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def password_change_done(request, id, template_name='registration/custom_password_change_done.html'):
    user_edit = get_object_or_404(User, pk=id)
    return render_to_response(template_name, {'user_this': user_edit}, context_instance=RequestContext(request))



### REPORTS ###########################################################################

def _user_events(from_date):
    return User.objects.all()\
                .filter(eventlog__create_dt__gte=from_date)\
                .annotate(event_count=Count('eventlog__pk'))

@staff_member_required
def user_activity_report(request, template_name='reports/user_activity.html'):
    now = datetime.now()
    users30days = _user_events(now-timedelta(days=10))
    users60days = _user_events(now-timedelta(days=60))
    users90days = _user_events(now-timedelta(days=90))
    # sort order of all fields for the upcoming response
    is_reverse = False
    is_ascending_username = True
    is_ascending_last_name = True
    is_ascending_first_name = True
    is_ascending_email = True
    is_ascending_events = True

    # get sort order
    sort = request.GET.get('sort', 'events')
    # Hande case if sort exists is one of the url parameters but blank
    if not sort:
        sort = 'events'

    if sort == 'username':
        users30days = users30days.order_by('username')
        users60days = users60days.order_by('username')
        users90days = users90days.order_by('username')
        is_ascending_username = False
    elif sort == '-username':
        users30days = users30days.order_by('-username')
        users60days = users60days.order_by('-username')
        users90days = users90days.order_by('-username')
        is_ascending_username = True
    elif sort == 'last_name':
        users30days = users30days.order_by('last_name')
        users60days = users60days.order_by('last_name')
        users90days = users90days.order_by('last_name')
        is_ascending_last_name = False
    elif sort == '-last_name':
        users30days = users30days.order_by('-last_name')
        users60days = users60days.order_by('-last_name')
        users90days = users90days.order_by('-last_name')
        is_ascending_last_name = True
    elif sort == 'first_name':
        users30days = users30days.order_by('first_name')
        users60days = users60days.order_by('first_name')
        users90days = users90days.order_by('first_name')
        is_ascending_first_name = False
    elif sort == '-first_name':
        users30days = users30days.order_by('-first_name')
        users60days = users60days.order_by('-first_name')
        users90days = users90days.order_by('-first_name')
        is_ascending_first_name = True
    elif sort == 'email':
        users30days = users30days.order_by('email')
        users60days = users60days.order_by('email')
        users90days = users90days.order_by('email')
        is_ascending_email = False
    elif sort == '-email':
        users30days = users30days.order_by('-email')
        users60days = users60days.order_by('-email')
        users90days = users90days.order_by('-email')
        is_ascending_email = True
    elif sort == 'events':
        users30days = users30days.order_by('-event_count')
        users60days = users60days.order_by('-event_count')
        users90days = users90days.order_by('-event_count')
        is_ascending_events = False
    elif sort == '-events':
        users30days = users30days.order_by('event_count')
        users60days = users60days.order_by('event_count')
        users90days = users90days.order_by('event_count')
        is_ascending_events = True

    # top 10 only
    users30days = users30days[:10]
    users60days = users60days[:10]
    users90days = users90days[:10]

    # Check for number sorting
    reverse = request.GET.get('reverse', 'False')
    if reverse == 'True':
        users30days = users30days[::-1]
        users60days = users60days[::-1]
        users90days = users90days[::-1]
        is_reverse = True
    else:
        is_reverse = False

    return render_to_response(template_name, {
        'users30days': users30days,
        'users60days': users60days,
        'users90days': users90days,
        'is_reverse': is_reverse,
        'is_ascending_username': is_ascending_username,
        'is_ascending_last_name': is_ascending_last_name,
        'is_ascending_first_name': is_ascending_first_name,
        'is_ascending_email': is_ascending_email,
        'is_ascending_events': is_ascending_events,
        }, context_instance=RequestContext(request))


@staff_member_required
def admin_users_report(request, template_name='reports/admin_users.html'):
    if not request.user.profile.is_superuser:
        raise Http403

    profiles = Profile.actives.filter(user__is_superuser=True).select_related()
    # sort order of all fields for the upcoming response
    is_ascending_id = True
    is_ascending_username = True
    is_ascending_last_name = True
    is_ascending_first_name = True
    is_ascending_email = True
    is_ascending_phone = True

    # get sort order
    sort = request.GET.get('sort', 'id')
    if sort == 'id':
        profiles = profiles.order_by('user__pk')
        is_ascending_id = False
    elif sort == '-id':
        profiles = profiles.order_by('-user__pk')
        is_ascending_id = True
    elif sort == 'username':
        profiles = profiles.order_by('user__username')
        is_ascending_username = False
    elif sort == '-username':
        profiles = profiles.order_by('-user__username')
        is_ascending_username = True
    elif sort == 'last_name':
        profiles = profiles.order_by('user__last_name')
        is_ascending_last_name = False
    elif sort == '-last_name':
        profiles = profiles.order_by('-user__last_name')
        is_ascending_last_name = True
    elif sort == 'first_name':
        profiles = profiles.order_by('user__first_name')
        is_ascending_first_name = False
    elif sort == '-first_name':
        profiles = profiles.order_by('-user__first_name')
        is_ascending_first_name = True
    elif sort == 'email':
        profiles = profiles.order_by('user__email')
        is_ascending_email = False
    elif sort == '-email':
        profiles = profiles.order_by('-user__email')
        is_ascending_email = True
    elif sort == 'phone':
        profiles = profiles.order_by('phone')
        is_ascending_phone = False
    elif sort == '-phone':
        profiles = profiles.order_by('-phone')
        is_ascending_phone = True

    return render_to_response(template_name, {
        'profiles': profiles,
        'is_ascending_id': is_ascending_id,
        'is_ascending_username': is_ascending_username,
        'is_ascending_last_name': is_ascending_last_name,
        'is_ascending_first_name': is_ascending_first_name,
        'is_ascending_email': is_ascending_email,
        'is_ascending_phone': is_ascending_phone,
        }, context_instance=RequestContext(request))

@staff_member_required
def user_access_report(request):
    now = datetime.now()
    logins_qs = EventLog.objects.filter(application="accounts",action="login")

    total_users = User.objects.all().count()
    total_logins = logins_qs.count()

    day_logins = []
    for days in [30, 60, 90, 120, 182, 365]:
        count = logins_qs.filter(create_dt__gte=now-timedelta(days=days)).values('user_id').distinct().count()
        day_logins.append((days, count))

    return render_to_response('reports/user_access.html', {
                  'total_users': total_users,
                  'total_logins': total_logins,
                  'day_logins': day_logins,},
                context_instance=RequestContext(request))

@login_required
def admin_list(request, template_name='profiles/admin_list.html'):
    # only admins can edit this list
    if not request.user.profile.is_superuser:
        raise Http403

    admins = Profile.actives.filter(user__is_superuser=True).select_related()

    return render_to_response(template_name, {'admins': admins},
                              context_instance=RequestContext(request))

@login_required
def users_not_in_groups(request, template_name='profiles/users_not_in_groups.html'):
    # superuser only
    if not request.user.profile.is_superuser:
        raise Http403

    # improve the query used to avoid timeouts
    users = User.objects.filter(group_member__isnull=True)

    # check if a user has profile. create a profile if no profile
    # exists for the user. This would be the self healing process.
    for usr in users:
        try:
            profile = usr.profile
        except Profile.DoesNotExist:
            Profile.objects.create_profile(user=usr)

    return render_to_response(template_name, {'users': users}, context_instance=RequestContext(request))

@login_required
def user_groups_edit(request, username, form_class=UserGroupsForm, template_name="profiles/add_delete_groups.html"):
    user = get_object_or_404(User, username=username)

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create_profile(user=user)

    if not profile.allow_edit_by(request.user):
        raise Http403

    if request.method == 'POST':
        form = form_class(user, request.user, request, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, _('Successfully edited groups for %(full_name)s' % { 'full_name' : user.get_full_name()}))
            return HttpResponseRedirect("%s%s" % (reverse('profile', args=[user.username]),'#userview-groups'))
    else:
        form = form_class(user, request.user, request)

    return render_to_response(template_name, {
                            'form': form,
                            'user_this': user,
                            }, context_instance=RequestContext(request))

@login_required
def user_role_edit(request, username, membership_id, form_class=GroupMembershipEditForm, template_name="profiles/edit_role.html"):
    user = get_object_or_404(User, username=username)
    membership = get_object_or_404(GroupMembership, id=membership_id)

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create_profile(user=user)

    if not profile.allow_edit_by(request.user):
        raise Http403

    if not has_perm(request.user,'user_groups.view_group', membership.group):
        raise Http403

    if request.method == 'POST':
        form = form_class(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, _('Successfully edited membership for %(g)s' % {'g':membership.group}))
            return HttpResponseRedirect("%s%s" % (reverse('profile', args=[user.username]),'#userview-groups'))
    else:
        form = form_class(instance=membership)

    return render_to_response(template_name, {
                            'form': form,
                            'membership': membership,
                            }, context_instance=RequestContext(request))

@login_required
def user_membership_add(request, username, form_class=UserMembershipForm, template_name="profiles/add_membership.html"):
    redirect_url = reverse('membership_default.add')
    redirect_url = '%s?username=%s' % (redirect_url, username)
    # this view is redundant and not handling membership add well.
    # redirect to membership add
    return redirect(redirect_url)

    user = get_object_or_404(User, username=username)

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create_profile(user=user)

    if not request.user.profile.is_superuser:
        raise Http403

    form = form_class(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            membership = form.save(commit=False)
            membership.user = user
            membership = update_perms_and_save(request, form, membership)
            messages.add_message(request, messages.SUCCESS, _('Successfully updated memberships for %s' % { 'full_name': user.get_full_name()}))
            membership.populate_or_clear_member_id()
            return HttpResponseRedirect("%s%s" % (reverse('profile', args=[user.username]),'#userview-memberships'))

    return render_to_response(template_name, {
                            'form': form,
                            'user_this': user,
                            }, context_instance=RequestContext(request))


@login_required
def similar_profiles(request, template_name="profiles/similar_profiles.html"):
    if not request.user.profile.is_superuser:
        raise Http403

    if request.method == 'POST':
        # generate a unique id for this import
        sid = str(int(time.time()))

        # store the info in the session to pass to the next page
        request.session[sid] = {'users': request.POST.getlist('id_users')}

        return HttpResponseRedirect(reverse('profile.merge_view', args=[sid]))

    users_with_duplicate_name = []
    users_with_duplicate_email = []

    # use raw sql to get the accurate number of duplicate names
    sql = """
            SELECT first_name , last_name
            FROM auth_user
            WHERE first_name <> '' and last_name <> ''
            GROUP BY first_name , last_name
            HAVING count(*) > 1
            ORDER BY last_name, first_name
        """
    cursor = connection.cursor()
    cursor.execute(sql)
    duplicate_names = cursor.fetchall()

    duplicate_emails = User.objects.values_list(
        'email', flat=True).annotate(
        num_emails=Count('email')).filter(num_emails__gt=1).exclude(email='').order_by('email')

    len_duplicate_names = len(duplicate_names)
    len_duplicate_emails = len(duplicate_emails)

    total_groups = len_duplicate_names + len_duplicate_emails
    num_groups_per_page = 20

    query = request.GET.get('q', u'')

    if query:
        curr_page = 1
        num_pages = 1
        page_range = []
    else:
        num_pages = int(math.ceil(total_groups * 1.0 / num_groups_per_page))
        try:
            curr_page = int(request.GET.get('page', 1))
        except:
            curr_page = 1
        if curr_page <= 0 or curr_page > num_pages:
            curr_page = 1
        page_range = get_pagination_page_range(num_pages, curr_page=curr_page)

        # slice the duplicate_names and duplicate_emails
        start_index = (curr_page - 1) * num_groups_per_page
        end_index = curr_page * num_groups_per_page
        if len_duplicate_names > 1:
            if start_index <= len_duplicate_names - 1:
                if end_index < len_duplicate_names:
                    duplicate_names = duplicate_names[start_index:end_index]
                else:
                    duplicate_names = duplicate_names[start_index:]
            else:
                duplicate_names = []

        if len_duplicate_emails > 1:
            if end_index < len_duplicate_names:
                duplicate_emails = []
            else:
                start_index = start_index - len_duplicate_names
                end_index = end_index - len_duplicate_names
                if start_index < 0:
                    start_index = 0

                if end_index > len_duplicate_emails:
                    end_index = len_duplicate_emails

                if start_index < end_index:
                    duplicate_emails = duplicate_emails[start_index:end_index]
                else:
                    duplicate_emails = []

    filtered_email_list = User.objects.values_list('email', flat=True)
    filtered_name_list = User.objects.values_list('first_name', flat=True)

    if query:
        filtered_email_list = filtered_email_list.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) |
            Q(last_name__icontains=query) | Q(email__icontains=query))

        filtered_name_list = filtered_name_list.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) |
            Q(last_name__icontains=query) | Q(email__icontains=query))

    for dup_name in duplicate_names:
        if dup_name[0] and dup_name[1] and dup_name[0] in filtered_name_list:
            users = User.objects.filter(
                first_name=dup_name[0],
                last_name=dup_name[1]).order_by('-last_login')
            users_with_duplicate_name.append(users)

    for email in duplicate_emails:
        if email and email in filtered_email_list:
            users = User.objects.filter(
                email=email).order_by('-last_login')
            users_with_duplicate_email.append(users)

    return render_to_response(template_name, {
        'users_with_duplicate_name': users_with_duplicate_name,
        'users_with_duplicate_email': users_with_duplicate_email,
        'curr_page': curr_page,
        'prev': curr_page - 1,
        'next': curr_page + 1,
        'num_pages': num_pages,
        'page_range': page_range,
        'user_this': None,
    }, context_instance=RequestContext(request))


@login_required
@password_required
def merge_profiles(request, sid, template_name="profiles/merge_profiles.html"):

    if not request.user.profile.is_superuser:
        raise Http403

    sid = str(sid)
    if not request.session.has_key(sid):
        return redirect("profile.similar")

    users_ids = (request.session[sid]).get('users', [])
    profiles = []
    for user_id in users_ids:
        profile = Profile.objects.get_or_create(user_id=user_id,
                                    defaults={
                                    'creator_id': request.user.id,
                                    'creator_username': request.user.username,
                                    'owner_id': request.user.id,
                                    'owner_username': request.user.username
                                    })[0]
        profiles.append(profile)
    form = ProfileMergeForm(request.POST or None,
                            list=(request.session[sid]).get('users', []))
    if request.method == 'POST':
        if form.is_valid():
            master = form.cleaned_data["master_record"]
            users = form.cleaned_data['user_list']
            
            master_user = master.user

            if master and users:
                # get description for event log before users get deleted
                description = 'Master user: %s, merged user(s): %s.' % (
                                '%s %s (%s)(id=%d)' % (master_user.first_name,
                                               master_user.last_name,
                                               master_user.username,
                                               master_user.id),
                                ', '.join(['%s %s (%s)(id=%d)' % (
                                profile.user.first_name,
                                profile.user.last_name,
                                profile.user.username,
                                profile.user.id
                                ) for profile in users if profile != master]))
        
                related = master_user._meta.get_fields()
                field_names = [field.name for field in master._meta.get_fields()]
        
                valnames = dict()
                for r in related:
                    if not r.related_model is Profile:
                        if not r.related_model:
                            continue
                        valnames.setdefault(r.related_model, []).append(r)
        
                for profile in users:
                    user_to_delete = profile.user
                    if profile != master:
                        for field in field_names:
                            if getattr(master, field) == '':
                                setattr(master, field, getattr(profile, field))
        
                        for model, fields in valnames.iteritems():
                            # skip auth_user
                            if model is User:
                                continue

                            for field in fields:
                                if isinstance(field, models.ManyToManyField):
                                    # handle ManyToMany
                                    items = eval('user_to_delete.%s.all()' % field.name)
                                    if items:
                                        for item in items:
                                            # add to master_user
                                            eval('master_user.%s.add(item)' % field.name)
                                        # clear from user_to_delete
                                        eval('user_to_delete.%s.clear()' % field.name)
                                    continue
                                
                                field_name = field.field.name
                                if not isinstance(field, models.OneToOneField) and not isinstance(field, models.OneToOneRel):
                                    objs = model.objects.filter(**{field_name: user_to_delete})
        
                                    # handle unique_together fields. for example, GroupMembership
                                    # unique_together = ('group', 'member',)
                                    [unique_together] = model._meta.unique_together[:1] or [None]
                                    if unique_together and field_name in unique_together:
                                        for obj in objs:
                                            field_values = [getattr(obj, fieldname) for fieldname in unique_together]
                                            field_dict = dict(zip(unique_together, field_values))
                                            # switch to master user
                                            field_dict[field_name] = master_user
                                            # check if the master record exists
                                            if model.objects.filter(**field_dict).exists():
                                                obj.delete()
                                            else:
                                                setattr(obj, field_name, master_user)
                                                obj.save()
                                    else:
                                        if objs.exists():
                                            try:
                                                objs.update(**{field_name: master_user})
                                            except Exception:
                                                connection._rollback()
                                else:  # OneToOne
                                    [obj] = model.objects.filter(**{field_name: user_to_delete})[:1] or [None]
                                    if obj:
                                        [master_obj] = model.objects.filter(**{field_name: master_user})[:1] or [None]
                                        if not master_obj:
                                            setattr(obj, field_name, master_user)
                                            obj.save()
                                        else:
                                            obj_fields = [field.name for field in master_obj._meta.get_fields()]
                                            updated = False
                                            for fld in obj_fields:
                                                master_val = getattr(master_obj, fld)
                                                if master_val == '' or master_val is None:
                                                    val = getattr(obj, fld)
                                                    if val != '' and not val is None:
                                                        setattr(master_obj, fld, val)
                                                        updated = True
                                            if updated:
                                                master_obj.save()
                                            # delete obj
                                            obj.delete()
        
                        master.save()
                        profile.delete()
                        user_to_delete.delete()
                        
        
                # log an event
                EventLog.objects.log(description=description[:120])
                #invalidate('profiles_profile')
                messages.add_message(request, messages.SUCCESS, _('Successfully merged users. %(desc)s' % { 'desc': description}))
        
            return redirect("profile.search")

    return render_to_response(template_name, {
        'form': form,
        'profiles': profiles,
    }, context_instance=RequestContext(request))



@login_required
@password_required
def profile_export(request, template_name="profiles/export.html"):
    """Export Profiles"""
    if not request.user.profile.is_staff:
        raise Http403

    form = ExportForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        export_fields = form.cleaned_data['export_fields']
        identifier = int(time.time())
        temp_file_path = 'export/profiles/%s_temp.csv' % identifier
        default_storage.save(temp_file_path, ContentFile(''))

        # start the process
        subprocess.Popen(["python", "manage.py",
                          "profile_export_process",
                          '--export_fields=%s' % export_fields,
                          '--identifier=%s' % identifier,
                          '--user=%s' % request.user.id])
        # log an event
        EventLog.objects.log()
        return HttpResponseRedirect(reverse('profile.export_status', args=[identifier]))

    context = {'form': form}
    return render_to_response(template_name, context, RequestContext(request))


@login_required
@password_required
def profile_export_status(request, identifier, template_name="profiles/export_status.html"):
    """Display export status"""
    if not request.user.profile.is_staff:
        raise Http403

    export_path = 'export/profiles/%s.csv' % identifier
    download_ready = False
    if default_storage.exists(export_path):
        download_ready = True
    else:
        temp_export_path = 'export/profiles/%s_temp.csv' % identifier
        if not default_storage.exists(temp_export_path) and \
                not default_storage.exists(export_path):
            raise Http404

    context = {'identifier': identifier,
               'download_ready': download_ready}
    return render_to_response(template_name, context, RequestContext(request))


@login_required
@password_required
def profile_export_download(request, identifier):
    """Download the profiles export."""
    if not request.user.profile.is_staff:
        raise Http403

    file_name = '%s.csv' % identifier
    file_path = 'export/profiles/%s' % file_name
    if not default_storage.exists(file_path):
        raise Http404

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=profiles_export_%s' % file_name
    response.content = default_storage.open(file_path).read()
    return response


@login_required
@password_required
def user_import_upload(request, template_name='profiles/import/upload.html'):
    """ Import users to the User and Profile. """

    if not request.user.profile.is_superuser:
        raise Http403

    form = UserUploadForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            user_import = form.save(commit=False)
            user_import.creator = request.user
            user_import.save()

            # redirect to preview page.
            return redirect(reverse('profiles.user_import_preview', args=[user_import.id]))

    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def user_import_preview(request, uimport_id, template_name='profiles/import/preview.html'):
    """ Preview the import. """

    if not request.user.profile.is_superuser:
        raise Http403

    #invalidate('profiles_userimport')
    uimport = get_object_or_404(UserImport, pk=uimport_id)
    if uimport.group_id:
        uimport.group = Group.objects.get(id=uimport.group_id)

    if uimport.status == 'preprocess_done':

        try:
            curr_page = int(request.GET.get('page', 1))
        except:
            curr_page = 1

        num_items_per_page = 10

        total_rows = UserImportData.objects.filter(uimport=uimport).count()

        # if total_rows not updated, update it
        if uimport.total_rows != total_rows:
            uimport.total_rows = total_rows
            uimport.save()
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
        data_list = UserImportData.objects.filter(
                                uimport=uimport,
                                row_num__gte=start_index,
                                row_num__lt=end_index).order_by(
                                    'row_num')

        users_list = []
        #print data_list
        imd = ImportUsers(request.user, uimport, dry_run=True)
        # to be efficient, we only process users on the current page
        fieldnames = None
        for idata in data_list:
            user_display = imd.process_user(idata)

            user_display['row_num'] = idata.row_num
            users_list.append(user_display)
            if not fieldnames:
                fieldnames = idata.row_data.keys()

        return render_to_response(template_name, {
            'uimport': uimport,
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
        if uimport.status in ('processing', 'completed'):
                return redirect(reverse('profiles.user_import_status',
                                     args=[uimport.id]))
        else:
            if uimport.status == 'not_started':
                subprocess.Popen(["python", "manage.py",
                              "users_import_preprocess",
                              str(uimport.pk)])

            return render_to_response(template_name, {
                'uimport': uimport,
                }, context_instance=RequestContext(request))


@login_required
def user_import_process(request, uimport_id):
    """ Process the import. """

    if not request.user.profile.is_superuser:
        raise Http403

    #invalidate('profiles_userimport')

    uimport = get_object_or_404(UserImport, pk=uimport_id)

    if uimport.status == 'preprocess_done':
        uimport.status = 'processing'
        uimport.num_processed = 0
        uimport.save()
        # start the process
        subprocess.Popen(["python", "manage.py",
                          "import_users",
                          str(uimport.pk),
                          str(request.user.pk)])

        # log an event
        EventLog.objects.log()

    # redirect to status page
    return redirect(reverse('profiles.user_import_status', args=[uimport.id]))


@login_required
def user_import_status(request, uimport_id, template_name='profiles/import/status.html'):
    """ Display import status. """

    if not request.user.profile.is_superuser:
        raise Http403
    #invalidate('profiles_userimport')
    uimport = get_object_or_404(UserImport,
                                    pk=uimport_id)
    if uimport.group_id:
        uimport.group = Group.objects.get(id=uimport.group_id)
    if uimport.status not in ('processing', 'completed'):
        return redirect(reverse('profiles.user_import'))

    return render_to_response(template_name, {
        'uimport': uimport,
    }, context_instance=RequestContext(request))


@login_required
def user_import_download_recap(request, uimport_id):
    """
    Download import recap.
    """

    if not request.user.profile.is_superuser:
        raise Http403
    #invalidate('profiles_userimport')
    uimport = get_object_or_404(UserImport,
                                    pk=uimport_id)
    uimport.generate_recap()
    filename = os.path.split(uimport.recap_file.name)[1]

    recap_path = uimport.recap_file.name
    if default_storage.exists(recap_path):
        response = HttpResponse(default_storage.open(recap_path).read(),
                                content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
    else:
        raise Http404


@csrf_exempt
@login_required
def user_import_get_status(request, uimport_id):
    """
    Get the import status and return as json
    """
    if not request.user.profile.is_superuser:
        raise Http403
    #invalidate('profiles_userimport')
    uimport = get_object_or_404(UserImport,
                                    pk=uimport_id)

    status_data = {'status': uimport.status,
                   'total_rows': str(uimport.total_rows),
                   'num_processed': str(uimport.num_processed)}

    if uimport.status == 'completed':
        summary_list = uimport.summary.split(',')
        status_data['num_insert'] = summary_list[0].split(':')[1]
        status_data['num_update'] = summary_list[1].split(':')[1]
        status_data['num_invalid'] = summary_list[2].split(':')[1]

    return HttpResponse(simplejson.dumps(status_data))


@csrf_exempt
@login_required
def user_import_check_preprocess_status(request, uimport_id):
    """
    Get the import encoding status
    """
    if not request.user.profile.is_superuser:
        raise Http403
    #invalidate('profiles_userimport')
    uimport = get_object_or_404(UserImport,
                                    pk=uimport_id)

    return HttpResponse(uimport.status)


@login_required
def download_user_template(request):
    """
    Download import template users
    """
    if not request.user.profile.is_superuser:
        raise Http403

    filename = "users_import_template.csv"

    title_list = ['salutation', 'first_name', 'last_name',
                         'initials', 'display_name', 'email',
                          'email2', 'address', 'address2',
                          'city', 'state', 'zipcode', 'country',
                         'company', 'position_title', 'department',
                         'phone', 'phone2', 'home_phone',
                         'work_phone', 'mobile_phone',
                         'fax', 'url', 'dob', 'spouse',
                         'direct_mail', 'notes', 'admin_notes',
                         'username', 'member_number']
    data_row_list = []

    return render_csv(filename, title_list,
                        data_row_list)


def activate_email(request):
    """
    Send an activation email to user to activate an inactive user account for a given an email address. 
    Optional parameter: username
    """
    from tendenci.apps.registration.models import RegistrationProfile
    from tendenci.apps.accounts.utils import send_registration_activation_email
    form = ActivateForm(request.GET)

    if form.is_valid():
        email = form.cleaned_data['email']
        username = form.cleaned_data['username']
        u = None
        if email and username:
            [u] = User.objects.filter(is_active=False, email=email, username=username)[:1] or [None]
            
        if email and not u:
            [u] = User.objects.filter(is_active=False, email=email).order_by('-is_active')[:1] or [None]

        if u:
            [rprofile] = RegistrationProfile.objects.filter(user=u)[:1] or [None]
            if rprofile and rprofile.activation_key_expired():
                rprofile.delete()
                rprofile = None
            if not rprofile:
                rprofile = RegistrationProfile.objects.create_profile(u)
            # send email
            send_registration_activation_email(u, rprofile, next=request.GET.get('next', ''))
            context = RequestContext(request)
            template_name = "profiles/activate_email.html"
            return render_to_response(template_name,
                              { 'email': email},
                              context_instance=context)

    raise Http404       
