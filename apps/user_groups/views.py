from datetime import datetime
from datetime import date

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.models import Site
from django.contrib import messages
from django.http import HttpResponse

from djcelery.models import TaskMeta
from base.http import Http403
from site_settings.utils import get_setting
from perms.utils import is_admin, get_notice_recipients, has_perm, get_query_filters, has_view_perm
from entities.models import Entity
from event_logs.models import EventLog
from event_logs.utils import request_month_range, day_bars
from event_logs.views import event_colors

from user_groups.models import Group, GroupMembership
from user_groups.forms import GroupForm, GroupMembershipForm
from user_groups.forms import GroupPermissionForm, GroupMembershipBulkForm
from user_groups.importer.forms import UploadForm
from user_groups.importer.tasks import ImportSubscribersTask

try:
    from notification import models as notification
except:
    notification = None

def search(request, template_name="user_groups/search.html"):
    """
    This page lists out all user groups.  If a search index
    is available, this page also allows you to search through
    user groups.
    """
    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)

    if has_index and query:
        groups = Group.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'groups.view_group')
        groups = Group.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            groups = groups.select_related()

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

def search_redirect(request):
    """
    This page redirects to the list page.  The list page can
    have a search feature if a search index is available.
    """
    return HttpResponseRedirect(reverse('groups'))

def group_detail(request, group_slug, template_name="user_groups/detail.html"):
    group = get_object_or_404(Group, slug=group_slug)

    if not has_view_perm(request.user,'user_groups.view_group',group): raise Http403
    
    log_defaults = {
        'event_id' : 165000,
        'event_data': '%s (%d) viewed by %s' % (group._meta.object_name, group.pk, request.user),
        'description': '%s viewed' % group._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': group,
    }
    EventLog.objects.log(**log_defaults)
    
    groupmemberships = GroupMembership.objects.filter(group=group).order_by('member__last_name')
    #members = group.members.all()
    count_members = len(groupmemberships)
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def group_add_edit(request, group_slug=None, 
                   form_class=GroupForm, 
                   template_name="user_groups/add_edit.html"):
    add, edit = False, False
    if group_slug:
        group = get_object_or_404(Group, slug=group_slug)
       
        if not has_perm(request.user,'user_groups.change_group',group):
            raise Http403
        title = "Edit Group"
        edit = True
    else:
        group = None
        if not has_perm(request.user,'user_groups.add_group'):raise Http403
        title = "Add Group"
        add = True

    if request.method == 'POST':
        if edit:
            form = form_class(request.POST, instance=group, user=request.user)
        else:
            form = form_class(request.POST, user=request.user)
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
            form = form_class(instance=group, user=request.user)
        else:
            form = form_class(user=request.user)
      
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
    
    if not has_perm(request.user,'user_groups.delete_group',group): raise Http403

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

def group_membership_self_add(request, slug, user_id):
    group = get_object_or_404(Group, slug=slug)
    user = get_object_or_404(User, pk=user_id)
    
    if not has_view_perm(request.user,'user_groups.view_group') and not group.allow_self_add:
        raise Http403
    
    group_membership = GroupMembership.objects.filter(member=user, group=group)
    
    if not group_membership:  
        group_membership = GroupMembership()
        
        group_membership.group = group
        group_membership.member = user
        group_membership.creator_id = user.id
        group_membership.creator_username = user.username
        group_membership.owner_id =  user.id
        group_membership.owner_username = user.username   
        
        group_membership.save()
    
        log_defaults = {
            'event_id' : 221000,
            'event_data': '%s (%d) added by %s' % (group_membership._meta.object_name, group_membership.pk, request.user),
            'description': '%s added' % group_membership._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': group_membership,
        }
        EventLog.objects.log(**log_defaults)     
        
        messages.add_message(request, messages.SUCCESS, 'Successfully added yourself to group %s' % group)
    else:
        messages.add_message(request, messages.INFO, 'You are already in the group %s' % group)
        
    return HttpResponseRedirect(reverse('group.search'))

def group_membership_self_remove(request, slug, user_id):
    group = get_object_or_404(Group, slug=slug)
    
    if not has_view_perm(request.user,'user_groups.view_group') and not group.allow_self_remove:
        raise Http403

    user = get_object_or_404(User, pk=user_id)
    
    group_membership = GroupMembership.objects.filter(member=user, group=group)
    
    if group_membership:
        group_membership = group_membership[0]
        if group_membership.member == user:
            log_defaults = {
                'event_id' : 223000,
                'event_data': '%s (%d) deleted by %s' % (group_membership._meta.object_name, group_membership.pk, request.user),
                'description': '%s deleted' % group_membership._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': group_membership,
            }
            EventLog.objects.log(**log_defaults)
            group_membership.delete()
            messages.add_message(request, messages.SUCCESS, 'Successfully removed yourself from group %s' % group)
    else:
        messages.add_message(request, messages.INFO, 'You are not in the group %s' % group)
                    
    return HttpResponseRedirect(reverse('group.search'))

def groupmembership_bulk_add(request, group_slug, 
                        form_class=GroupMembershipBulkForm,
                        template_name="user_groups/member_add.html"):
    group = get_object_or_404(Group, slug=group_slug)
    
    if request.method == 'POST':
        form = form_class(group, request.POST)
        if form.is_valid():
            members = form.cleaned_data['members']
            
            old_members = GroupMembership.objects.filter(group=group)
            
            #delete removed groupmemberships
            if members:
                for old_m in old_members:
                    try:
                        members.get(pk=old_m.member.pk)
                    except User.DoesNotExist:
                        log_defaults = {
                            'event_id' : 223000,
                            'event_data': '%s (%d) deleted by %s' % (old_m._meta.object_name, old_m.pk, request.user),
                            'description': '%s deleted' % old_m._meta.object_name,
                            'user': request.user,
                            'request': request,
                            'instance': old_m,
                        }
                        EventLog.objects.log(**log_defaults)
                        old_m.delete()
            else: #when members is None
                for old_m in old_members:
                    log_defaults = {
                        'event_id' : 223000,
                        'event_data': '%s (%d) deleted by %s' % (old_m._meta.object_name, old_m.pk, request.user),
                        'description': '%s deleted' % old_m._meta.object_name,
                        'user': request.user,
                        'request': request,
                        'instance': old_m,
                    }
                    EventLog.objects.log(**log_defaults)
                    old_m.delete()
                    
            for m in members:
                try:
                    group_membership = GroupMembership.objects.get(group=group, member=m)
                except GroupMembership.DoesNotExist:
                    group_membership = GroupMembership(group=group, member=m)
                    group_membership.creator_id = request.user.id
                    group_membership.creator_username = request.user.username
                
                group_membership.role=form.cleaned_data['role']
                group_membership.status=form.cleaned_data['status']
                group_membership.status_detail=form.cleaned_data['status_detail']
                group_membership.owner_id =  request.user.id
                group_membership.owner_username = request.user.username
                
                group_membership.save()

                log_defaults = {
                    'event_id' : 221000,
                    'event_data': '%s (%d) added by %s' % (group_membership._meta.object_name, group_membership.pk, request.user),
                    'description': '%s added' % group_membership._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': group_membership,
                }
                EventLog.objects.log(**log_defaults)
            return HttpResponseRedirect(group.get_absolute_url())
    else:
        member_label = request.GET.get('member_label', 'username')
        form = form_class(group, member_label=member_label)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
    
def groupmembership_add_edit(request, group_slug, user_id=None, 
                             form_class=GroupMembershipForm, 
                             template_name="user_groups/member_add_edit.html"):
    add, edit = None, None
    group = get_object_or_404(Group, slug=group_slug)
    
    if user_id:
        user = get_object_or_404(User, pk=user_id)
        group_membership = get_object_or_404(GroupMembership, member=user, group=group)
        if not has_perm(request.user,'user_groups.change_groupmembership',group_membership):
            raise Http403
        edit = True
    else:
        group_membership = None
        if not has_perm(request.user,'user_groups.add_groupmembership'):
            raise Http403
        add = True

    if request.method == 'POST':
        form = form_class(None, user_id, request.POST, instance=group_membership)
        if form.is_valid():
            group_membership = form.save(commit=False)
            group_membership.group = group
            if not group_membership.id:
                group_membership.creator_id = request.user.id
                group_membership.creator_username = request.user.username
            group_membership.owner_id =  request.user.id
            group_membership.owner_username = request.user.username

            group_membership.save()
            if add:
                log_defaults = {
                    'event_id' : 221000,
                    'event_data': '%s (%d) added by %s' % (group_membership._meta.object_name, group_membership.pk, request.user),
                    'description': '%s added' % group_membership._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': group_membership,
                }
                EventLog.objects.log(**log_defaults)                
            if edit:
                log_defaults = {
                    'event_id' : 222000,
                    'event_data': '%s (%d) edited by %s' % (group_membership._meta.object_name, group_membership.pk, request.user),
                    'description': '%s edited' % group_membership._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': group_membership,
                }
                EventLog.objects.log(**log_defaults)
                            
            
            return HttpResponseRedirect(group.get_absolute_url())
    else:
        form = form_class(group, user_id, instance=group_membership)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def groupmembership_delete(request, group_slug, user_id, template_name="user_groups/member_delete.html"):
    group = get_object_or_404(Group, slug=group_slug)
    user = get_object_or_404(User, pk=user_id)
    group_membership = get_object_or_404(GroupMembership, group=group, member=user)
    if not has_perm(request.user,'user_groups.delete_groupmembership',group_membership):
        raise Http403
    
    if request.method == 'POST':
        log_defaults = {
            'event_id' : 223000,
            'event_data': '%s (%d) deleted by %s' % (group_membership._meta.object_name, group_membership.pk, request.user),
            'description': '%s deleted' % group_membership._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': group_membership,
        }
        EventLog.objects.log(**log_defaults)
        group_membership.delete()
        messages.add_message(request, messages.SUCCESS, 'Successfully removed %s from group %s' % (user.get_full_name(), group))
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

def group_member_export(request, group_slug):
    """
    Export all group members for a specific group
    """
    group = get_object_or_404(Group, slug=group_slug)

    # if they can edit it, they can export it
    if not has_perm(request.user,'user_groups.change_group', group):
        raise Http403

    import xlwt
    from ordereddict import OrderedDict
    from django.db import connection

    # create the excel book and sheet
    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet('Group Members')
    
    # the key is what the column will be in the
    # excel sheet. the value is the database lookup
    # Used OrderedDict to maintain the column order
    group_mappings = OrderedDict([
        ('user_id', 'au.id'),
        ('first_name', 'au.first_name'),
        ('last_name', 'au.last_name'),
        ('email', 'au.email'),
        ('receives email', 'pp.direct_mail'),
        ('company', 'pp.company'),
        ('address', 'pp.address'),
        ('address2', 'pp.address2'),
        ('city', 'pp.city'),
        ('state', 'pp.state'),
        ('zipcode', 'pp.zipcode'),
        ('country', 'pp.country'),
        ('phone', 'pp.phone'),
        ('is_active', 'au.is_active'),
        ('date', 'gm.create_dt'),
    ])
    group_lookups = ','.join(group_mappings.values())

    # Use custom sql to fetch the rows because we need to
    # populate the user profiles information and you
    # cannot do that with django's ORM without using
    # get_profile() for each user query
    # pulling 13,000 group members can be done in one
    # query using Django's ORM but then you need
    # 13,000 individual queries :(
    cursor = connection.cursor()
    sql = "SELECT %s FROM user_groups_groupmembership gm \
           INNER JOIN auth_user au ON (au.id = gm.member_id) \
           LEFT OUTER JOIN profiles_profile pp \
           on (pp.user_id = gm.member_id) WHERE group_id = %%s;"
    sql =  sql % group_lookups
    cursor.execute(sql, [group.pk])
    values_list = list(cursor.fetchall())

    # Append the heading to the list of values that will
    # go into the excel sheet
    values_list.insert(0, group_mappings.keys())
    
    # excel date styles
    default_style = xlwt.Style.default_style
    datetime_style = xlwt.easyxf(num_format_str='mm/dd/yyyy hh:mm')
    date_style = xlwt.easyxf(num_format_str='mm/dd/yyyy')

    if values_list:
        # Write the data enumerated to the excel sheet
        for row, row_data in enumerate(values_list):
            for col, val in enumerate(row_data):
                # styles the date/time fields
                if isinstance(val, datetime):
                    style = datetime_style
                elif isinstance(val, date):
                    style = date_style
                else:
                    style = default_style
                sheet.write(row, col, val, style=style)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=group_%s_member_export.xls' % group.pk
    book.save(response)
    return response

def group_subscriber_export(request, group_slug):
    """
    Export all group members for a specific group
    """
    group = get_object_or_404(Group, slug=group_slug)
    
    # if they can edit it, they can export it
    if not has_perm(request.user,'user_groups.change_group', group):
        raise Http403
    
    import xlwt
    from ordereddict import OrderedDict
    from django.db import connection
    from forms_builder.forms.models import FieldEntry
    
    # create the excel book and sheet
    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet('Group Subscribers')
    
    # excel date styles
    default_style = xlwt.Style.default_style
    datetime_style = xlwt.easyxf(num_format_str='mm/dd/yyyy hh:mm')
    date_style = xlwt.easyxf(num_format_str='mm/dd/yyyy')
    
    entries = FieldEntry.objects.filter(entry__subscriptions__group=group).distinct()
    row_index = {}
    col_index = {}
    
    for entry in entries:
        val = entry.value
        
        if entry.entry.pk in row_index:
            # get the subscriber's row number
            row = row_index[entry.entry.pk]
        else:
            # assign the row if it is not yet available
            row = len(row_index.keys()) + 1
            row_index[entry.entry.pk] = row
            
        if entry.field.label in col_index:
            # get the entry's col number
            col = col_index[entry.field.label]
        else:
            # assign the col if it is not yet available
            # and label the new column
            col = len(col_index.keys())
            col_index[entry.field.label] = col
            sheet.write(0, col, entry.field.label, style=default_style)
            
        # styles the date/time fields
        if isinstance(val, datetime):
            style = datetime_style
        elif isinstance(val, date):
            style = date_style
        else:
            style = default_style
        
        sheet.write(row, col, val, style=style)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=group_%s_subscriber_export.xls' % group.pk
    book.save(response)
    return response

def group_all_export(request, group_slug):
    """
    Export all group members for a specific group
    """
    group = get_object_or_404(Group, slug=group_slug)

    # if they can edit it, they can export it
    if not has_perm(request.user,'user_groups.change_group', group):
        raise Http403

    import xlwt
    from ordereddict import OrderedDict
    from django.db import connection
    from forms_builder.forms.models import FieldEntry

    # create the excel book and sheet
    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet('Group Members and Subscribers')
    
    #initialize indexes
    row_index = {}
    col_index = {}
    
    #---------
    # MEMBERS
    #---------
    # excel date styles
    default_style = xlwt.Style.default_style
    datetime_style = xlwt.easyxf(num_format_str='mm/dd/yyyy hh:mm')
    date_style = xlwt.easyxf(num_format_str='mm/dd/yyyy')
    
    # the key is what the column will be in the
    # excel sheet. the value is the database lookup
    # Used OrderedDict to maintain the column order
    group_mappings = OrderedDict([
        ('user_id', 'au.id'),
        ('first_name', 'au.first_name'),
        ('last_name', 'au.last_name'),
        ('email', 'au.email'),
        ('receives email', 'pp.direct_mail'),
        ('company', 'pp.company'),
        ('address', 'pp.address'),
        ('address2', 'pp.address2'),
        ('city', 'pp.city'),
        ('state', 'pp.state'),
        ('zipcode', 'pp.zipcode'),
        ('country', 'pp.country'),
        ('phone', 'pp.phone'),
        ('is_active', 'au.is_active'),
        ('date', 'gm.create_dt'),
    ])
    group_lookups = ','.join(group_mappings.values())

    # Use custom sql to fetch the rows because we need to
    # populate the user profiles information and you
    # cannot do that with django's ORM without using
    # get_profile() for each user query
    # pulling 13,000 group members can be done in one
    # query using Django's ORM but then you need
    # 13,000 individual queries :(
    cursor = connection.cursor()
    sql = "SELECT %s FROM user_groups_groupmembership gm \
           INNER JOIN auth_user au ON (au.id = gm.member_id) \
           LEFT OUTER JOIN profiles_profile pp \
           on (pp.user_id = gm.member_id) WHERE group_id = %%s;"
    sql =  sql % group_lookups
    cursor.execute(sql, [group.pk])
    values_list = list(cursor.fetchall())

    # index the group key mappings and insert them into the sheet.
    for key in group_mappings.keys():
        if not key in col_index:
            col = len(col_index.keys())
            col_index[key] = col
            sheet.write(0, col, key, style=default_style)

    if values_list:
        # Write the data enumerated to the excel sheet
        for row, row_data in enumerate(values_list):
            for col, val in enumerate(row_data):
                
                if not row in row_index:
                    # assign the row if it is not yet available
                    row_index[row] = row + 1
                
                # styles the date/time fields
                if isinstance(val, datetime):
                    style = datetime_style
                elif isinstance(val, date):
                    style = date_style
                else:
                    style = default_style
                
                sheet.write(row + 1, col, val, style=style)
    
    #-------------
    # Subscribers
    #-------------
    entries = FieldEntry.objects.filter(entry__subscriptions__group=group).distinct()
    
    for entry in entries:
        val = entry.value
        field = entry.field.label.lower().replace(" ", "_")
        
        if "subscriber %s" % str(entry.entry.pk) in row_index:
            # get the subscriber's row number
            row = row_index["subscriber %s" % str(entry.entry.pk)]
        else:
            # assign the row if it is not yet available
            row = len(row_index.keys()) + 1
            row_index["subscriber %s" % str(entry.entry.pk)] = row
        
        if field in col_index:
            # get the entry's col number
            col = col_index[field]
        else:
            # assign the col if it is not yet available
            # and label the new column
            col = len(col_index.keys())
            col_index[field] = col
            sheet.write(0, col, field, style=default_style)
            
        # styles the date/time fields
        if isinstance(val, datetime):
            style = datetime_style
        elif isinstance(val, date):
            style = date_style
        else:
            style = default_style
        
        sheet.write(row, col, val, style=style)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=group_%s_all_export.xls' % group.pk
    book.save(response)
    return response

def group_subscriber_import(request, group_slug, form_class=UploadForm, template="user_groups/import_subscribers.html"):
    """
    Import subscribers for a specific group
    """
    group = get_object_or_404(Group, slug=group_slug)
    
    # if they can edit, they can export
    if not has_perm(request.user,'user_groups.change_group', group):
        raise Http403

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            csv = form.save(commit=False)
            csv.group = group
            csv.creator = request.user
            csv.creator_username = request.user.username
            csv.owner = request.user
            csv.owner_username = request.user.username
            csv.save()
            
            if not settings.CELERY_IS_ACTIVE:
                # if celery server is not present 
                # evaluate the result and render the results page
                result = ImportSubscribersTask()
                subs = result.run(group, csv.file.path)
                return render_to_response('user_groups/import_subscribers_result.html', {
                    'group':group,
                    'subs':subs,
                }, context_instance=RequestContext(request))
            else:
                result = ImportSubscribersTask.delay(group, csv.file.path)
                return redirect('subscribers_import_status', group.slug, result.task_id)
    else:
        form = form_class()
    
    return render_to_response(template, {
        'group':group,
        'form':form,
    }, context_instance=RequestContext(request))

@login_required
def subscribers_import_status(request, group_slug, task_id, template_name='user_groups/import_status.html'):
    """
    Checks if a subscriber import is completed.
    """
    group = get_object_or_404(Group, slug=group_slug)
    
    if not is_admin(request.user):
        raise Http403
    
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        #tasks database entries are not created at once.
        task = None
    
    if task and task.status == "SUCCESS":
        subs = task.result
        return render_to_response('user_groups/import_subscribers_result.html', {
            'group':group,
            'subs':subs,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response(template_name, {
            'group':group,
            'task':task,
        }, context_instance=RequestContext(request))
