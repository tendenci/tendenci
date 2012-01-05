# django
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import ugettext as _
from django.db.models import get_app
from django.core.exceptions import ImproperlyConfigured
from django.contrib import messages
# for password change
from django.views.decorators.csrf import csrf_protect

from base.decorators import ssl_required

from perms.object_perms import ObjectPermission
from perms.utils import (has_perm, is_admin, update_perms_and_save,
    get_notice_recipients)
from base.http import Http403
from event_logs.models import EventLog
from site_settings.utils import get_setting

# for avatar
from avatar.models import Avatar, avatar_file_path
from avatar.forms import PrimaryAvatarForm

# for group memberships
from user_groups.models import GroupMembership
from user_groups.forms import GroupMembershipEditForm

from profiles.models import Profile
from profiles.forms import (ProfileForm, UserPermissionForm, 
    UserGroupsForm, ValidatingPasswordChangeForm, UserMembershipForm)
from profiles.utils import user_add_remove_admin_auth_group

try:
    notification = get_app('notification')
except ImproperlyConfigured:
    notification = None
    
friends = False
#if 'friends' in settings.INSTALLED_APPS:
#    friends = True
#    from friends.models import Friendship

# view profile  
@login_required 
def index(request, username='', template_name="profiles/index.html"):
    if not username:
        username = request.user.username
    user_this = get_object_or_404(User, username=username)

    try:
        profile = user_this.get_profile()
    except Profile.DoesNotExist:
        profile = Profile.objects.create_profile(user=user_this)
        
    # security check 
    if not profile.allow_view_by(request.user): 
        raise Http403

    # content counts
    content_counts = {'total':0, 'invoice':0}
    from django.db.models import Q
    from invoices.models import Invoice
    inv_count = Invoice.objects.filter(Q(creator=user_this) | (Q(owner=user_this))).count()
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

    try:
        # memberships
        memberships = user_this.memberships.all()
    except:
        memberships = None

    log_defaults = {
        'event_id' : 125000,
        'event_data': '%s (%d) viewed by %s' % (profile._meta.object_name, profile.pk, request.user),
        'description': '%s viewed' % profile._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': profile,
    }
    EventLog.objects.log(**log_defaults)
 
    return render_to_response(template_name, {
        "user_this": user_this,
        "profile":profile,
        'content_counts': content_counts,
        'additional_owners': additional_owners,
        'group_memberships': group_memberships,
        'memberships': memberships,
        }, context_instance=RequestContext(request))


def search(request, template_name="profiles/search.html"):
    # check if allow anonymous user search
    allow_anonymous_search = get_setting('module', 'users', 'allowanonymoususersearchuser')
    allow_user_search = get_setting('module', 'users', 'allowusersearch')

    if request.user.is_anonymous():
        if not allow_anonymous_search:
            raise Http403
    
    if request.user.is_authenticated():
        if not allow_user_search and not is_admin(request.user):
            raise Http403

    query = request.GET.get('q', None)
    profiles = Profile.objects.search(query, user=request.user)
    profiles = profiles.order_by('last_name_exact')

    log_defaults = {
        'event_id' : 124000,
        'event_data': '%s searched by %s' % ('Profile', request.user),
        'description': '%s searched' % 'Profile',
        'user': request.user,
        'request': request,
        'source': 'profiles'
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {'profiles':profiles, "user_this":None}, 
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
            if is_admin(request.user):
                security_level = form.cleaned_data['security_level']
                if security_level == 'developer':
                    new_user.is_superuser = 1
                    new_user.is_staff = 1
                elif security_level == 'admin':
                    new_user.is_superuser = 0
                    new_user.is_staff = 1
                    
                    # add them to admin auth group
                    user_add_remove_admin_auth_group(new_user)
                        
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
                
            if interactive == 1:
                new_user.is_active = 1
            else:
                new_user.is_active = 0

            profile.save()
            new_user.save()
            
            log_defaults = {
                'event_id' : 121000,
                'event_data': '%s (%d) added by %s' % (new_user._meta.object_name, new_user.pk, request.user),
                'description': '%s added' % new_user._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': new_user,
            }
            EventLog.objects.log(**log_defaults)
            
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
           
            if is_admin(request.user):
                security_level = form.cleaned_data['security_level']
                
                if security_level == 'developer':
                    user_edit.is_superuser = 1
                    user_edit.is_staff = 1
                    # remove them from auth_group if any - they don't need it
                    user_edit.groups = []
                elif security_level == 'admin':
                    user_edit.is_superuser = 0
                    user_edit.is_staff = 1
                    
                    # add them to admin auth group
                    user_add_remove_admin_auth_group(user_edit)
                else:
                    user_edit.is_superuser = 0
                    user_edit.is_staff = 0
                    # remove them from auth_group if any
                    user_edit.groups = []
                    
                # add them to admin auth group
                user_add_remove_admin_auth_group(user_edit)
                    
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
               
            profile.save()
            user_edit.save()
            
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
            

            log_defaults = {
                'event_id' : 122000,
                'event_data': '%s (%d) edited by %s' % (user_edit._meta.object_name, user_edit.pk, request.user),
                'description': '%s edited' % user_edit._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': user_edit,
            }
            EventLog.objects.log(**log_defaults)
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

        log_defaults = {
            'event_id' : 123000,
            'event_data': '%s (%d) deleted by %s' % (user._meta.object_name, user.pk, request.user),
            'description': '%s deleted' % user._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': user,
        }
        EventLog.objects.log(**log_defaults)
        
        
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
    if not request.user.is_superuser: raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST, request.user, instance=user_edit)
    else:
        form = form_class(instance=user_edit)
    if form.is_valid():
        user_edit.is_superuser = form.cleaned_data['is_superuser']
        user_edit.user_permissions = form.cleaned_data['user_permissions']
        user_edit.save()
        return HttpResponseRedirect(reverse('profile', args=[user_edit.username]))
   
    return render_to_response(template_name, {'user_this':user_edit, 'profile':profile, 'form':form}, 
        context_instance=RequestContext(request))
    
    
#@login_required
#def edit_user_groups(request, id, template_name="profiles/edit_groups.html"):
#    user_edit = get_object_or_404(User, pk=id)
#    profile = user_edit.get_profile()
#    
#    # get the groups with permissions
#    groups = Group.objects.search(user=request.user)
#    groups = [g.object for g in groups.filter(allow_self_add=True)]
#    groups = [g for g in groups if not g.is_member(user_edit)]
#    
#    if is_admin(request.user):
#        groups = Group.objects.all()
#    
#    print 'groups', groups
#    
#    # groups the user is in that have allow_self_remove true
#    groups_joined = user_edit.group_set.filter(allow_self_remove=True)
#    
#    if is_admin(request.user):
#        groups_joined = user_edit.group_set.all()
#    
#    print 'groups_joined', groups_joined
#
#    if request.method == "POST":
#        selected_groups = request.POST.getlist("user_groups")    # list of ids
#        selected_groups = [Group.objects.get(id=g) for g in selected_groups] # list of objects
#        
#        print 'selected_groups', selected_groups
#        
#        groups_to_add = [g for g in selected_groups if g not in groups_joined]
#        print 'groups_to_add', groups_to_add
#        for g in groups_to_add:
#            gm = GroupMembership(group=g, member=user_edit)
#            gm.creator_id = request.user.id
#            gm.creator_username = request.user.username
#            gm.owner_id = request.user.id
#            gm.owner_username = request.user.username
#            gm.save()    
#            log_defaults = {
#                'event_id' : 221000,
#                'event_data': '%s (%d) added by %s' % (gm._meta.object_name, gm.pk, request.user),
#                'description': '%s added' % gm._meta.object_name,
#                'user': request.user,
#                'request': request,
#                'instance': gm,
#            }
#            EventLog.objects.log(**log_defaults)    
#
#        # remove those not selected but already in GroupMembership 
#        groups_to_check = [groups_joined] + selected_groups 
#        print 'groups_to_check', groups_to_check
#        groups_to_remove = [g for g in groups_joined if g not in groups_to_check]
#        print 'groups_to_remove', groups_to_remove
#        for g in groups_to_remove:
#            gm = GroupMembership.objects.get(group=g, member=user_edit)
#            log_defaults = {
#                'event_id' : 223000,
#                'event_data': '%s (%d) deleted by %s' % (gm._meta.object_name, gm.pk, request.user),
#                'description': '%s deleted' % gm._meta.object_name,
#                'user': request.user,
#                'request': request,
#                'instance': gm,
#            }
#            EventLog.objects.log(**log_defaults)            
#            
#            gm.delete()
#            
#    return render_to_response(template_name, {'user_this':user_edit, 'profile':profile, 'groups':groups, 'groups_joined':groups_joined}, 
#        context_instance=RequestContext(request))
 
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
            request.user.message_set.create(
                message=_("Successfully uploaded a new avatar."))
        if 'choice' in request.POST and primary_avatar_form.is_valid():
            avatar = Avatar.objects.get(id=
                primary_avatar_form.cleaned_data['choice'])
            avatar.primary = True
            avatar.save()
            updated = True
            request.user.message_set.create(
                message=_("Successfully updated your avatar."))
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
        post_change_redirect = reverse('profiles.views.password_change_done', kwargs={'id':id})
    if request.method == "POST":
        form = password_change_form(user=user_edit, data=request.POST)
        if is_admin(request.user):
            del form.fields['old_password']
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=user_edit)
        # an admin doesn't have to enter the old password
        if is_admin(request.user):
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
                .annotate(event_count=Count('eventlog__pk'))\
                .order_by('-event_count')

@staff_member_required
def user_activity_report(request):
    now = datetime.now()
    users30days = _user_events(now-timedelta(days=10))[:10]
    users60days = _user_events(now-timedelta(days=60))[:10]
    users90days = _user_events(now-timedelta(days=90))[:10]
    return render_to_response(
                'reports/user_activity.html', 
                {'users30days': users30days,'users60days': users60days,'users90days': users90days,},  
                context_instance=RequestContext(request))


@staff_member_required
def admin_users_report(request):
    users = User.objects.all().filter(is_superuser=True)
    return render_to_response(
                'reports/admin_users.html', 
                {'users': users},  
                context_instance=RequestContext(request))


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
    if not is_admin(request.user):
        raise Http403

    filters = {
        'status':1,
        'status_detail':'active',
        'user__is_staff': 1,
        'user__is_active': 1,
    }
    admins = Profile.objects.filter(**filters)
    
    return render_to_response(template_name, {'admins': admins},
                              context_instance=RequestContext(request))

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
            messages.add_message(request, messages.INFO, 'Successfully edited groups for %s' % user.get_full_name())
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
            messages.add_message(request, messages.INFO, 'Successfully edited membership for %s' % membership.group)
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
        
    if not profile.allow_edit_by(request.user):
        raise Http403
        
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership = update_perms_and_save(request, form, membership)
            messages.add_message(request, messages.INFO, 'Successfully updated memberships for %s' % user.get_full_name())
            return HttpResponseRedirect("%s%s" % (reverse('profile', args=[user.username]),'#userview-memberships'))
    else:
        form = form_class(initial={'user':user})

    return render_to_response(template_name, {
                            'form': form,
                            'user_this': user,
                            }, context_instance=RequestContext(request))
