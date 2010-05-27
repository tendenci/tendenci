from django.shortcuts import get_object_or_404, render_to_response
from django.core.paginator import QuerySetPaginator
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.models import User

from usergroups.models import Group, GroupMembership
from usergroups.forms import GroupForm, GroupMembershipForm

def group_search(request, template_name="usergroups/group_search.html"):
    groups = Group.objects.all()
    return render_to_response(template_name, {'groups':groups}, 
        context_instance=RequestContext(request))
    
def group_detail(request, group_slug, template_name="usergroups/group_detail.html"):
    group = get_object_or_404(Group, slug=group_slug)
    members = group.members.all()
    count_members = len(members)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def group_add_edit(request, group_slug=None, 
                   form_class=GroupForm, 
                   template_name="usergroups/group_form.html"):
    if group_slug:
        group = get_object_or_404(Group, slug=group_slug)
        title = "Edit Group"
    else:
        group = None
        title = "Add Group"

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=group)
        if form.is_valid():
            group = form.save(commit=False)
            if not group.id:
                group.creator = request.user
                group.creator_username = request.user.username
            group.owner =  request.user
            group.owner_username = request.user.username
            group = form.save()
            
            return HttpResponseRedirect(group.get_absolute_url())
    else:
        form = form_class(instance=group)
      
    return render_to_response(template_name, {'form':form, 'titie':title, 'group':group}, context_instance=RequestContext(request))


def groupmembership_add_edit(request, group_slug, user_id=None, 
                             form_class=GroupMembershipForm, 
                             template_name="usergroups/groupmembership_form.html"):

    group = get_object_or_404(Group, slug=group_slug)
   
    if user_id:
        user = get_object_or_404(User, pk=user_id)
        groupmembership = get_object_or_404(GroupMembership, member=user, group=group)
    else:
        groupmembership = None

    if request.method == 'POST':
        form = form_class(request.POST, instance=groupmembership)
        if form.is_valid():
            groupmembership = form.save(commit=False)
            groupmembership.group = group
            if not groupmembership.id:
                groupmembership.creator_id = request.user.id
                groupmembership.creator_username = request.user.username
            groupmembership.owner_id =  request.user.id
            groupmembership.owner_username = request.user.username
            
            groupmembership.save()
            return HttpResponseRedirect(group.get_absolute_url())
    else:

        form = form_class(instance=groupmembership)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def groupmembership_delete(request, groupmembership_id, template_name="usergroups/groupmembership_confirm_delete.html"):

    groupmembership = get_object_or_404(GroupMembership, pk=groupmembership_id)

    if request.method == 'POST':
        group = groupmembership.group
        groupmembership.delete()
        return HttpResponseRedirect(group.get_absolute_url())
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
