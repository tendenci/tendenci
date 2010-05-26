# django
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404

from django.contrib.auth.models import User

from profiles.models import Profile
from profiles.forms import ProfileForm, ProfileEditForm, UserForm, UserEditForm

# Create your views here.
def profiles(request, template_name="profiles/profiles.html"):
    return render_to_response(template_name, {}, 
                              context_instance=RequestContext(request))
 
# view profile  
@login_required 
def index(request, id, template_name="profiles/index.html"):
    user_view = get_object_or_404(User, pk=id)
    try:
        #profile = Profile.objects.get(user=user)
        profile = user_view.get_profile()
    except Profile.DoesNotExist:
        profile, created = Profile.objects.get_or_create(user=user_view)
        
    return render_to_response(template_name, {"user_view":user_view, "profile":profile }, 
                              context_instance=RequestContext(request))
 
@login_required   
def search(request, template_name="profiles/search.html"):
    profiles = Profile.objects.all()
    #print profiles
   
    return render_to_response(template_name, {'profiles':profiles}, 
        context_instance=RequestContext(request))


@permission_required('users.add_user')
def add(request, form_class=ProfileForm, form_class2=UserForm, template_name="profiles/add.html"):
    if request.method == "POST":
        #form_user = form_class2(request.user, request.POST)
        form = form_class(request.POST, request.user)
        form2 = form_class2(request.POST, request.user)
        
        if form.is_valid() and form2.is_valid():
            profile = form.save(request)
            new_user = profile.user
            new_user.is_superuser = form2.cleaned_data['is_superuser']
            new_user.groups = form2.cleaned_data['groups']
            new_user.user_permissions = form2.cleaned_data['user_permissions']
            new_user.save()
            
            return HttpResponseRedirect(reverse('profile', args=[new_user.pk]))
    else:
        form = form_class()
        form2 = form_class2()

    return render_to_response(template_name, {'form':form, 'form2':form2}, 
        context_instance=RequestContext(request))
    
@permission_required('users.change_user')
def edit(request, id, form_class=ProfileEditForm, form_class2=UserEditForm, template_name="profiles/edit.html"):
    user_edit = get_object_or_404(User, pk=id)
    try:
        profile = Profile.objects.get(user=user_edit)
        
    except Profile.DoesNotExist:
        profile, created = Profile.objects.get_or_create(user=user_edit)
        
    if request.method == "POST":
        #form_user = form_class2(request.user, request.POST)
        if profile:
            form = form_class(request.POST, request.user, instance=profile)
        else:
            form = form_class(request.POST, request.user)
        form2 = form_class2(request.POST, request.user, instance=user_edit)
        
        if form.is_valid() and form2.is_valid():
            profile = form.save(request, user_edit)
            user_edit.is_superuser = form2.cleaned_data['is_superuser']
            user_edit.groups = form2.cleaned_data['groups']
            user_edit.user_permissions = form2.cleaned_data['user_permissions']
            user_edit.save()
            
            return HttpResponseRedirect(reverse('profile', args=[user_edit.pk]))
    else:
        if profile:
            form = form_class(instance=profile)
        else:
            form = form_class()
        form2 = form_class2(instance=user_edit)

    return render_to_response(template_name, {'user_edit':user_edit, 'profile':profile, 'form':form, 'form2':form2}, 
        context_instance=RequestContext(request))
    
@permission_required('users.delete_user')
def delete(request, id, template_name="profiles/delete.html"):
    user = get_object_or_404(User, pk=id)
    profile = Profile.objects.get(user=user)

    if request.method == "POST":
        profile.delete()
        user.delete()
        return HttpResponseRedirect(reverse('profile.search'))

    return render_to_response(template_name, {'profile': profile}, 
        context_instance=RequestContext(request))
   