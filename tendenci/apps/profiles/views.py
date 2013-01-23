# django
from datetime import datetime, timedelta
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
from django.contrib import messages
from django.conf import settings
# for password change
from django.views.decorators.csrf import csrf_protect

from djcelery.models import TaskMeta
from johnny.cache import invalidate

from tendenci.core.base.decorators import ssl_required

from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.perms.utils import (has_perm, update_perms_and_save, get_notice_recipients, get_query_filters)
from tendenci.core.base.http import Http403
from tendenci.core.event_logs.models import EventLog
from tendenci.core.site_settings.utils import get_setting

# for avatar
from avatar.models import Avatar, avatar_file_path
from avatar.forms import PrimaryAvatarForm

# for group memberships
from tendenci.apps.user_groups.models import GroupMembership
from tendenci.apps.user_groups.forms import GroupMembershipEditForm

from tendenci.apps.profiles.models import Profile
from tendenci.apps.profiles.forms import (ProfileForm, ExportForm, UserPermissionForm, 
UserGroupsForm, ValidatingPasswordChangeForm, UserMembershipForm)
from tendenci.apps.profiles.tasks import ExportProfilesTask
from tendenci.addons.events.models import Registrant

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
        profile = user_this.get_profile()
    except Profile.DoesNotExist:
        profile = Profile.objects.create_profile(user=user_this)

    if not profile.allow_view_by(request.user):
        raise Http403

    # content counts
    content_counts = {'total': 0, 'invoice': 0}
    from tendenci.apps.invoices.models import Invoice
    inv_count = Invoice.objects.filter(Q(creator=user_this) | Q(owner=user_this), Q(bill_to_email=user_this.email)).count()
    if request.user.profile.is_superuser:
        inv_count = Invoice.objects.filter(Q(creator=user_this) | Q(owner=user_this) | Q(bill_to_email=user_this.email)).count()
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
    group_memberships = user_this.group_member.all()

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
        }, context_instance=RequestContext(request))


def search(request, template_name="profiles/search.html"):
    # check if allow anonymous user search
    allow_anonymous_search = get_setting('module', 'users', 'allowanonymoususersearchuser')
    allow_user_search = get_setting('module', 'users', 'allowusersearch')
    membership_view_perms = get_setting('module', 'memberships', 'memberprotection')

    if request.user.is_anonymous():
        if not allow_anonymous_search:
            raise Http403

    if request.user.is_authenticated():
        if not allow_user_search and not request.user.profile.is_superuser:
            raise Http403

    members = request.GET.get('members', None)
    query = request.GET.get('q', None)
    filters = get_query_filters(request.user, 'profiles.view_profile')
    profiles = Profile.objects.filter(Q(status=True), Q(status_detail="active"), Q(filters)).distinct()

    if query:
        profiles = profiles.filter(Q(status=True), Q(status_detail="active"), Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(user__email__icontains=query) | Q(user__username__icontains=query) | Q(display_name__icontains=query) | Q(company__icontains=query))

    is_not_member_filter = (Q(member_number="") | Q(user__is_active=False))
    if members:
        if not request.user.profile.is_superuser:
            if membership_view_perms == "private":
                profiles = profiles.filter(is_not_member_filter)
            elif membership_view_perms == "all-members" or membership_view_perms == "member-type":
                if request.user.profile and request.user.profile.is_member:
                    profiles = profiles.exclude(is_not_member_filter)
                else:
                    profiles = profiles.filter(is_not_member_filter)
            else:
                profiles = profiles.exclude(is_not_member_filter)
        else:
            profiles = profiles.exclude(is_not_member_filter)
    else:
        if not request.user.profile.is_superuser:
            if membership_view_perms == "private":
                    profiles = profiles.filter(is_not_member_filter)
            elif membership_view_perms == "all-members" or membership_view_perms == "member-type":
                if not request.user.profile or not request.user.profile.is_member:
                    profiles = profiles.filter(is_not_member_filter)

    if not request.user.profile.is_superuser:
        profiles = profiles.exclude(hide_in_search=True)

    profiles = profiles.order_by('user__last_name', 'user__first_name')

    EventLog.objects.log()
    return render_to_response(template_name, {'profiles': profiles, "user_this": None},
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
    if not request.user.profile.is_superuser: raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST, request.user, instance=user_edit)
    else:
        form = form_class(instance=user_edit)
    if form.is_valid():
        user_edit.is_superuser = form.cleaned_data['is_superuser']
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
   
@login_required
def change_avatar(request, id, extra_context={}, next_override=None):
    user_edit = get_object_or_404(User, pk=id)
    try:
        profile = Profile.objects.get(user=user_edit)
    except Profile.DoesNotExist:
        profile = Profile.objects.create_profile(user=user_edit)
        
    #if not has_perm(request.user,'profiles.change_profile',profile): raise Http403
    if not profile.allow_edit_by(request.user): raise Http403
    
    avatars = Avatar.objects.filter(user=user_edit).order_by('-primary')
    if avatars.count() > 0:
        avatar = avatars[0]
        kwargs = {'initial': {'choice': avatar.id}}
    else:
        avatar = None
        kwargs = {}
    primary_avatar_form = PrimaryAvatarForm(request.POST or None, user=user_edit, **kwargs)
    if request.method == "POST":
        updated = False
        if 'avatar' in request.FILES:
            path = avatar_file_path(user=user_edit, 
                filename=request.FILES['avatar'].name)
            avatar = Avatar(
                user = user_edit,
                primary = True,
                avatar = path,
            )
            new_file = avatar.avatar.storage.save(path, request.FILES['avatar'])
            avatar.save()
            updated = True

            messages.add_message(
                request, messages.SUCCESS, _("Successfully uploaded a new avatar."))

        if 'choice' in request.POST and primary_avatar_form.is_valid():
            avatar = Avatar.objects.get(id=
                primary_avatar_form.cleaned_data['choice'])
            avatar.primary = True
            avatar.save()
            updated = True

            messages.add_message(
                request, messages.SUCCESS, _("Successfully updated your avatar."))

        if updated and notification:
            notification.send([request.user], "avatar_updated", {"user": user_edit, "avatar": avatar})
            #if friends:
            #    notification.send((x['friend'] for x in Friendship.objects.friends_for_user(user_edit)), "avatar_friend_updated", {"user": user_edit, "avatar": avatar})
        return HttpResponseRedirect(reverse('profile', args=[user_edit.username]))
        #return HttpResponseRedirect(next_override or _get_next(request))
    return render_to_response(
        'profiles/change_avatar.html',
        extra_context,
        context_instance = RequestContext(
            request,
            {'user_this': user_edit,
              'avatar': avatar, 
              'avatars': avatars,
              'primary_avatar_form': primary_avatar_form,
              'next': next_override or _get_next(request), }
        )
    )
    
@ssl_required    
@csrf_protect
@login_required
def password_change(request, id, template_name='registration/password_change_form.html',
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
def password_change_done(request, id, template_name='registration/password_change_done.html'):
    user_edit = get_object_or_404(User, pk=id)
    return render_to_response(template_name, {'user_this': user_edit},  context_instance=RequestContext(request))



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
    logins_qs = EventLog.objects.filter(event_id=125200)
    
    total_users = User.objects.all().count()
    total_logins = logins_qs.count()
    
    day_logins = []
    for days in [30, 60, 90, 120, 182, 365]:
        count = logins_qs.filter(create_dt__gte=now-timedelta(days=days)).count()
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

    users = []
    for user in User.objects.all():
        if not user.profile.get_groups():
            users.append(user)
    
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
            messages.add_message(request, messages.SUCCESS, 'Successfully edited groups for %s' % user.get_full_name())
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
            messages.add_message(request, messages.SUCCESS, 'Successfully edited membership for %s' % membership.group)
            return HttpResponseRedirect("%s%s" % (reverse('profile', args=[user.username]),'#userview-groups'))
    else:
        form = form_class(instance=membership)

    return render_to_response(template_name, {
                            'form': form,
                            'membership': membership,
                            }, context_instance=RequestContext(request))

@login_required
def user_membership_add(request, username, form_class=UserMembershipForm, template_name="profiles/add_membership.html"):
    user = get_object_or_404(User, username=username)
    
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create_profile(user=user)
        
    if not request.user.profile.is_superuser:
        raise Http403
        
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership = update_perms_and_save(request, form, membership)
            messages.add_message(request, messages.SUCCESS, 'Successfully updated memberships for %s' % user.get_full_name())
            membership.populate_or_clear_member_id()
            return HttpResponseRedirect("%s%s" % (reverse('profile', args=[user.username]),'#userview-memberships'))
    else:
        form = form_class(initial={'user':user})

    return render_to_response(template_name, {
                            'form': form,
                            'user_this': user,
                            }, context_instance=RequestContext(request))

@login_required
def export(request, template_name="profiles/export.html"):
    """Create a csv file for all the users
    """

    if not request.user.profile.is_staff:
        raise Http404

    if request.method == 'POST':
        form = ExportForm(request.POST, user=request.user)
        if form.is_valid():
            if not settings.CELERY_IS_ACTIVE:
                task = ExportProfilesTask()
                response = task.run()
                return response
            else:
                task = ExportProfilesTask.delay()
                task_id = task.task_id
                return redirect('profile.export_status', task_id)
    else:
        form = ExportForm(user=request.user)
        
    return render_to_response(template_name, {
        'form':form,
        'user_this':None,
    }, context_instance=RequestContext(request))


def export_status(request, task_id, template_name="profiles/export_status.html"):
    invalidate('celery_taskmeta')
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        task = None

    return render_to_response(template_name, {
        'task':task,
        'task_id':task_id,
        'user_this':None,
    }, context_instance=RequestContext(request))


def export_check(request, task_id):
    invalidate('celery_taskmeta')
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        task = None

    if task and task.status == "SUCCESS":
        return HttpResponse("OK")
    else:
        return HttpResponse("DNE")


def export_download(request, task_id):
    invalidate('celery_taskmeta')
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        task = None

    if task and task.status == "SUCCESS":
        return task.result
    else:
        raise Http404
