# django
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.models import User

# for password change
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.csrf import csrf_protect


# for avatar
from avatar.models import Avatar, avatar_file_path
from avatar.forms import PrimaryAvatarForm
from django.utils.translation import ugettext as _
from django.db.models import get_app
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

try:
    notification = get_app('notification')
except ImproperlyConfigured:
    notification = None
    
friends = False
if 'friends' in settings.INSTALLED_APPS:
    friends = True
    from friends.models import Friendship

from profiles.models import Profile
from profiles.forms import ProfileForm, UserForm, UserEditForm, UserPermissionForm

from base.http import render_to_403

from user_groups.models import Group, GroupMembership
 
# view profile  
@login_required 
def index(request, username="", template_name="profiles/index.html"):
    print username
    if not username:
        username = request.user.username
    user_this = get_object_or_404(User, username=username)
    
    try:
        #profile = Profile.objects.get(user=user)
        profile = user_this.get_profile()
        #if not request.user.has_perm('profiles.view_profile', profile):return render_to_403()
    except Profile.DoesNotExist:
        profile = Profile.objects.create_profile(user=user_this)
        
    return render_to_response(template_name, {"user_this": user_this, "profile":profile,
                                              "user_objs":{"user_this": user_this } }, 
                              context_instance=RequestContext(request))
 
@login_required   
def search(request, template_name="profiles/search.html"):
    users = User.objects.all()
   
    return render_to_response(template_name, {'users':users, "user_this":None}, 
        context_instance=RequestContext(request))


@login_required
def add(request, form_class=ProfileForm, template_name="profiles/add.html"):
    if not request.user.has_perm('profiles.add_profile'):return render_to_403()
    
    if request.method == "POST":
        #form_user = form_class2(request.user, request.POST)
        form = form_class(None, request.POST, request.user)
        #form2 = form_class2(request.POST, request.user)
        
        if form.is_valid():
            profile = form.save(request, None)
            new_user = profile.user
            security_level = form.cleaned_data['security_level']
            if security_level == 'developer':
                new_user.is_superuser = 1
                new_user.is_staff = 1
            elif security_level == 'admin':
                new_user.is_superuser = 1
                new_user.is_staff = 0
            else:
                new_user.is_superuser = 0
                new_user.is_staff = 0
           
            new_user.save()
            
            return HttpResponseRedirect(reverse('profile', args=[new_user.username]))
    else:
        form = form_class(None)
        #form2 = form_class2()
       
    return render_to_response(template_name, {'form':form, 'user_this':None}, 
        context_instance=RequestContext(request))
    

@login_required
def edit(request, id, form_class=ProfileForm, template_name="profiles/edit.html"):
    user_edit = get_object_or_404(User, pk=id)
    
    try:
        profile = Profile.objects.get(user=user_edit)
        if not request.user.has_perm('profiles.change_profile', profile): return render_to_403()
    except Profile.DoesNotExist:
        profile = Profile.objects.create_profile(user=user_edit)
        if not request.user.has_perm('profiles.change_profile', profile): return render_to_403()
        
    if request.method == "POST":
        #form_user = form_class2(request.user, request.POST)
        if profile:
            form = form_class(user_edit, request.POST, request.user, instance=profile)
        else:
            form = form_class(user_edit, request.POST, request.user )
        #form2 = form_class2(request.POST, request.user, instance=user_edit)
        
        if form.is_valid():
            profile = form.save(request, user_edit)
            #user_edit.is_superuser = form2.cleaned_data['is_superuser']
            #user_edit.groups = form2.cleaned_data['groups']
            #user_edit.user_permissions = form2.cleaned_data['user_permissions']
            security_level = form.cleaned_data['security_level']
            
            if security_level == 'developer':
                user_edit.is_superuser = 1
                user_edit.is_staff = 1
            elif security_level == 'admin':
                user_edit.is_superuser = 1
                user_edit.is_staff = 0
            else:
                user_edit.is_superuser = 0
                user_edit.is_staff = 0
            user_edit.save()
            
            return HttpResponseRedirect(reverse('profile', args=[user_edit.username]))
    else:
        if profile:
            form = form_class(user_edit, instance=profile)
            
        else:
            form = form_class(user_edit,)
        #form2 = form_class2(instance=user_edit)

    return render_to_response(template_name, {'user_this':user_edit, 'profile':profile, 'form':form,}, 
        context_instance=RequestContext(request))
    

def delete(request, id, template_name="profiles/delete.html"):
    user = get_object_or_404(User, pk=id)
    try:
        profile = Profile.objects.get(user=user)
    except:
        profile = None
    
    if not request.user.has_perm('profiles.delete_profile', profile): return render_to_403()

    if request.method == "POST":
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
    profile = user_edit.get_profile()
    
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
    
    
@login_required
def edit_user_groups(request, id, template_name="profiles/edit_groups.html"):
    user_edit = get_object_or_404(User, pk=id)
    profile = user_edit.get_profile()
    # a list of groups - need to figure out which ones to pull based on user's security level. 
    groups = Group.objects.all()
    # a list of groups this user in
    groups_joined = user_edit.group_set.all()

    if request.method == "POST":
        selected_groups = request.POST.getlist("user_groups")    # list of ids
        
        selected_groups = [Group.objects.get(id=g) for g in selected_groups] # list of objects
        groups_to_add = [g for g in selected_groups if g not in groups_joined]
        for g in groups_to_add:
            gm = GroupMembership(group=g, member=user_edit)
            gm.creator_id = request.user.id
            gm.creator_username = request.user.username
            gm.owner_id = request.user.id
            gm.owner_username = request.user.username
            gm.save()    
        # remove those not selected but already in GroupMembership  
        groups_to_remove = [g for g in groups_joined if g not in selected_groups]
        for g in groups_to_remove:
            gm = GroupMembership.objects.get(group=g, member=user_edit)
            gm.delete()
        groups_joined = user_edit.group_set.all()
        #print new_groups
        #print request.POST 
    return render_to_response(template_name, {'user_this':user_edit, 'profile':profile, 'groups':groups, 'groups_joined':groups_joined}, 
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
            if friends:
                notification.send((x['friend'] for x in Friendship.objects.friends_for_user(user_edit)), "avatar_friend_updated", {"user": user_edit, "avatar": avatar})
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
    
    
@csrf_protect
@login_required
def password_change(request, id, template_name='registration/password_change_form.html',
                    post_change_redirect=None, password_change_form=PasswordChangeForm):
    user_edit = get_object_or_404(User, pk=id)
    if post_change_redirect is None:
        post_change_redirect = reverse('profiles.views.password_change_done', args=(id))
    if request.method == "POST":
        form = password_change_form(user=user_edit, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=user_edit)
    return render_to_response(template_name, {
        'user_this': user_edit,
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def password_change_done(request, id, template_name='registration/password_change_done.html'):
    user_edit = get_object_or_404(User, pk=id)
    return render_to_response(template_name, {'user_this': user_edit},  context_instance=RequestContext(request))
