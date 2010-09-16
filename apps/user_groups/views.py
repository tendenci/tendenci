from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from user_groups.models import Group, GroupMembership
from user_groups.forms import GroupForm, GroupMembershipForm, GroupPermissionForm
from base.http import Http403
from perms.utils import is_admin
from event_logs.models import EventLog
from perms.utils import get_notice_recipients
from entities.models import Entity
from event_logs.utils import request_month_range, day_bars
from event_logs.views import event_colors

try:
    from notification import models as notification
except:
    notification = None

def group_search(request, template_name="user_groups/search.html"):
    query = request.GET.get('q', None)
    
    if is_admin(request.user):
        groups = Group.objects.search(query)
    else:
        if request.user.has_perm('user_groups.view_group'):
            groups = Group.objects.search(query).filter(show_as_option=1, allow_self_add=1, 
                                                        status=1, status_detail='active')
        else:
            if not request.user.is_anonymous():
                groups = Group.objects.search(query).filter(show_as_option=1, allow_self_add=1, 
                                                            status=1, status_detail='active',
                                                            allow_user_view=1)
            else:
                groups = Group.objects.search(query).filter(show_as_option=1, allow_self_add=1, 
                                                            status=1, status_detail='active',
                                                            allow_anonymous_view=1)

    log_defaults = {
        'event_id' : 164000,
        'event_data': '%s searched by %s' % ('Group', request.user),
        'description': '%s searched' % 'Group',
        'user': request.user,
        'request': request,
        'source': 'user_groups'
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {'groups':groups}, 
        context_instance=RequestContext(request))
    
def group_detail(request, group_slug, template_name="user_groups/detail.html"):
    group = get_object_or_404(Group, slug=group_slug)
    
    if not request.user.has_perm('user_groups.view_group', group): raise Http403
    
    log_defaults = {
        'event_id' : 165000,
        'event_data': '%s (%d) viewed by %s' % (group._meta.object_name, group.pk, request.user),
        'description': '%s viewed' % group._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': group,
    }
    EventLog.objects.log(**log_defaults)
    
    groupmemberships = GroupMembership.objects.filter(group=group).order_by('sort_order')
    #members = group.members.all()
    count_members = len(groupmemberships)
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def group_add_edit(request, group_slug=None, 
                   form_class=GroupForm, 
                   template_name="user_groups/add_edit.html"):
    add, edit = False, False
    if group_slug:
        group = get_object_or_404(Group, slug=group_slug)
       
        if not request.user.has_perm('user_groups.change_group', group):
            raise Http403
        title = "Edit Group"
        edit = True
    else:
        group = None
        if not request.user.has_perm('user_groups.add_group'):raise Http403
        title = "Add Group"
        add = True

    if request.method == 'POST':
        if edit:
            form = form_class(request.user, request.POST, instance=group)
        else:
            form = form_class(request.user, request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            if not group.id:
                group.creator = request.user
                group.creator_username = request.user.username
                
            # set up user permission
            group.allow_user_view, group.allow_user_edit = form.cleaned_data['user_perms']
                            
            group.owner =  request.user
            group.owner_username = request.user.username
            group = form.save()
            
            if add:
                # send notification to administrators
                recipients = get_notice_recipients('module', 'groups', 'grouprecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': group,
                            'request': request,
                        }
                        notification.send_emails(recipients,'group_added', extra_context)
                    
                log_defaults = {
                    'event_id' : 161000,
                    'event_data': '%s (%d) added by %s' % (group._meta.object_name, group.pk, request.user),
                    'description': '%s added' % group._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': group,
                }
                EventLog.objects.log(**log_defaults)                
            if edit:
                log_defaults = {
                    'event_id' : 162000,
                    'event_data': '%s (%d) edited by %s' % (group._meta.object_name, group.pk, request.user),
                    'description': '%s edited' % group._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': group,
                }
                EventLog.objects.log(**log_defaults)
                
            return HttpResponseRedirect(group.get_absolute_url())
    else:
        if edit:
            form = form_class(request.user, instance=group)
        else:
            form = form_class(request.user)
      
    return render_to_response(template_name, {'form':form, 'titie':title, 'group':group}, context_instance=RequestContext(request))


@login_required
def group_edit_perms(request, id, form_class=GroupPermissionForm, template_name="user_groups/edit_perms.html"):
    group_edit = get_object_or_404(Group, pk=id)
    
    if request.method == "POST":
        form = form_class(request.POST, request.user, instance=group_edit)
    else:
        form = form_class(instance=group_edit)
       
    if form.is_valid():
        group_edit.permissions = form.cleaned_data['permissions']
        group_edit.save()
        return HttpResponseRedirect(group_edit.get_absolute_url())
   
    return render_to_response(template_name, {'group':group_edit, 'form':form}, 
        context_instance=RequestContext(request))
    
def group_delete(request, id, template_name="user_groups/delete.html"):
    group = get_object_or_404(Group, pk=id)
    
    if not request.user.has_perm('user_groups.delete_group', group): raise Http403

    if request.method == "POST":
        # send notification to administrators
        recipients = get_notice_recipients('module', 'groups', 'grouprecipients')
        if recipients: 
            if notification:
                extra_context = {
                    'object': group,
                    'request': request,
                }
                notification.send_emails(recipients,'group_deleted', extra_context)
                    
        log_defaults = {
            'event_id' : 163000,
            'event_data': '%s (%d) deleted by %s' % (group._meta.object_name, group.pk, request.user),
            'description': '%s deleted' % group._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': group,
        }
        EventLog.objects.log(**log_defaults)

        group.delete()
        return HttpResponseRedirect(reverse('group.search'))

    return render_to_response(template_name, {'group':group}, 
        context_instance=RequestContext(request))

def groupmembership_add_edit(request, group_slug, user_id=None, 
                             form_class=GroupMembershipForm, 
                             template_name="user_groups/member_add_edit.html"):
    add, edit = None, None
    group = get_object_or_404(Group, slug=group_slug)
    
    if user_id:
        user = get_object_or_404(User, pk=user_id)
        groupmembership = get_object_or_404(GroupMembership, member=user, group=group)
        if not request.user.has_perm('user_groups.change_groupmembership', groupmembership):
            raise Http403
        edit = True
    else:
        groupmembership = None
        if not request.user.has_perm('user_groups.add_groupmembership'):
            raise Http403
        add = True

    if request.method == 'POST':
        form = form_class(None, user_id, request.POST, instance=groupmembership)
        if form.is_valid():
            groupmembership = form.save(commit=False)
            groupmembership.group = group
            if not groupmembership.id:
                groupmembership.creator_id = request.user.id
                groupmembership.creator_username = request.user.username
            groupmembership.owner_id =  request.user.id
            groupmembership.owner_username = request.user.username

            groupmembership.save()
            if add:
                log_defaults = {
                    'event_id' : 221000,
                    'event_data': '%s (%d) added by %s' % (groupmembership._meta.object_name, groupmembership.pk, request.user),
                    'description': '%s added' % groupmembership._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': groupmembership,
                }
                EventLog.objects.log(**log_defaults)                
            if edit:
                log_defaults = {
                    'event_id' : 222000,
                    'event_data': '%s (%d) edited by %s' % (groupmembership._meta.object_name, groupmembership.pk, request.user),
                    'description': '%s edited' % groupmembership._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': groupmembership,
                }
                EventLog.objects.log(**log_defaults)
                            
            
            return HttpResponseRedirect(group.get_absolute_url())
    else:

        form = form_class(group, user_id, instance=groupmembership)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def groupmembership_delete(request, group_slug, user_id, template_name="user_groups/member_delete.html"):
    group = get_object_or_404(Group, slug=group_slug)
    user = get_object_or_404(User, pk=user_id)
    groupmembership = get_object_or_404(GroupMembership, group=group, member=user)
    if not request.user.has_perm('user_groups.delete_groupmembership', groupmembership):
        raise Http403
    
    if request.method == 'POST':
        log_defaults = {
            'event_id' : 223000,
            'event_data': '%s (%d) deleted by %s' % (groupmembership._meta.object_name, groupmembership.pk, request.user),
            'description': '%s deleted' % groupmembership._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': groupmembership,
        }
        EventLog.objects.log(**log_defaults)
        groupmembership.delete()
        return HttpResponseRedirect(group.get_absolute_url())
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def _events_chart(from_date, to_date, event_ids):
    "Returns events charts for provided date range and event ids"
    
    data = EventLog.objects.all()\
            .filter(create_dt__gte=from_date)\
            .filter(create_dt__lte=to_date)\
            .filter(event_id__in=event_ids)\
            .extra(select={'day':'DATE(create_dt)'})\
            .values('day', 'event_id')\
            .annotate(count=Count('pk'))\
            .order_by('day', 'event_id')
    return day_bars(data, from_date.year, from_date.month, 100, event_colors)
    

@staff_member_required
def users_added_report(request, kind):
    
    if kind == 'added':
        event_ids = (121000, 121100, 123001, 123103)
        title = 'Site Users Added Report'
    elif kind == 'referral':
        event_ids = (125114, 125115)
        title = 'Contacts Report - Referral Analysis Report (all contacts)'
    else:
        raise NotImplementedError('kind "%s" not supported' % kind)
    
    from_date, to_date = request_month_range(request)
    queryset = EventLog.objects.all()
    queryset = queryset.filter(create_dt__gte=from_date)
    queryset = queryset.filter(create_dt__lte=to_date)
    
    chart_data = _events_chart(from_date, to_date, event_ids)
    
    data = queryset.filter(event_id=221000)\
            .filter()\
            .values('headline')\
            .annotate(count=Count('pk'))\
            .order_by('-count')

    return render_to_response('reports/users_added.html', 
                              {'data': data, 'chart_data': chart_data,
                               'report_title': title,
                               'entities': Entity.objects.all().order_by('entity_name'),
                               'site': Site.objects.get_current(),
                               'date_range': (from_date, to_date)}, 
                              context_instance=RequestContext(request))
