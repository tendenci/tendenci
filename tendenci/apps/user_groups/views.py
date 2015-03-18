import subprocess
from datetime import datetime
from datetime import date
import time as ttime
from djcelery.models import TaskMeta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.models import Site
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import Http404
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from tendenci.core.base.http import Http403
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.decorators import superuser_required
from tendenci.core.perms.utils import get_notice_recipients, has_perm, get_query_filters, has_view_perm
from tendenci.core.imports.forms import ImportForm
from tendenci.core.imports.models import Import
from tendenci.core.imports.utils import extract_from_excel, render_excel
from tendenci.apps.entities.models import Entity
from tendenci.core.event_logs.models import EventLog
from tendenci.core.event_logs.utils import request_month_range, day_bars
from tendenci.core.event_logs.views import event_colors
from tendenci.apps.user_groups.models import Group, GroupMembership
from tendenci.apps.user_groups.forms import GroupForm, GroupMembershipForm, GroupSearchForm
from tendenci.apps.user_groups.forms import GroupForm, GroupMembershipForm, MessageForm
from tendenci.apps.user_groups.forms import GroupPermissionForm, GroupMembershipBulkForm
#from tendenci.apps.user_groups.importer.forms import UploadForm
#from tendenci.apps.user_groups.importer.tasks import ImportSubscribersTask
from tendenci.apps.user_groups.importer.utils import user_groups_import_process
from tendenci.apps.notifications import models as notification
from tendenci.core.base.utils import get_deleted_objects


def search(request, template_name="user_groups/search.html"):
    """
    This page lists out all user groups.  If a search index
    is available, this page also allows you to search through
    user groups.
    """
    query = request.GET.get('q', None)
    form = GroupSearchForm(request.GET)
    cat = None

    filters = get_query_filters(request.user, 'groups.view_group', perms_field=False)
    groups = Group.objects.filter(filters).distinct()

    if request.user.is_authenticated():
        groups = groups.select_related()

    if form.is_valid():
        cat = form.cleaned_data['search_category']

        if query and cat:
            groups = groups.filter(**{cat: query} )

    groups = groups.order_by('slug')

    EventLog.objects.log()

    return render_to_response(template_name, {'groups':groups, 'form': form},
        context_instance=RequestContext(request))

def search_redirect(request):
    """
    This page redirects to the list page.  The list page can
    have a search feature if a search index is available.
    """
    return HttpResponseRedirect(reverse('groups'))

@login_required
def group_detail(request, group_slug, template_name="user_groups/detail.html"):
    group = get_object_or_404(Group, slug=group_slug)

    if not has_view_perm(request.user,'user_groups.view_group',group):
        raise Http403

    if group in request.user.profile.get_groups():
        is_group_member = True
        gm = GroupMembership.objects.get(group=group, member=request.user)
    else:
        is_group_member = False
        gm = None

    EventLog.objects.log(instance=group)

    groupmemberships = GroupMembership.objects.filter(
        group=group,
        status=True,
        status_detail='active').order_by('member__last_name')

    count_members = len(groupmemberships)
    return render_to_response(
        template_name,
        locals(),
        context_instance=RequestContext(request))

@superuser_required
def message(request, group_slug, template_name='user_groups/message.html'):
    """
    Send a message to the group
    """
    from tendenci.core.emails.models import Email

    group = get_object_or_404(Group, slug=group_slug)
    EventLog.objects.log(instance=group)

    members = GroupMembership.objects.filter(
        group=group,
        status=True,
        status_detail='active')

    num_members = members.count()

    form = MessageForm(request.POST or None,
        request=request,
        num_members=num_members)


    if request.method == 'POST' and form.is_valid():

        email = Email()
        email.sender_display = request.user.get_full_name()
        email.sender = get_setting('site', 'global', 'siteemailnoreplyaddress')
        email.reply_to = email.sender
        email.content_type = 'text/html'
        email.subject = form.cleaned_data['subject']
        email.body = form.cleaned_data['body']
        email.save(request.user)

        # send email to myself (testing email)
        if form.cleaned_data['is_test']:
            email.recipient = request.user.email
            email.send()

            messages.add_message(
                request,
                messages.SUCCESS,
                _('Successfully sent test email to yourself'))

            EventLog.objects.log(instance=email)

        else:
            # send email to members
            for member in members:
                email.recipient = member.member.email
                email.send()

            messages.add_message(
                request,
                messages.SUCCESS,
                _('Successfully sent email to all %(num)s members in this group' % {'num': num_members}))

            EventLog.objects.log(instance=email)

        return redirect('group.detail', group_slug=group_slug)

    else:
        print 'form errors', form.errors.items()


    return render(request, template_name, {
        'group': group,
        'num_members': num_members,
        'form': form})


def group_add_edit(request, group_slug=None,
                   form_class=GroupForm,
                   template_name="user_groups/add_edit.html"):
    add, edit = False, False
    if group_slug:
        group = get_object_or_404(Group, slug=group_slug)

        if not has_perm(request.user,'user_groups.change_group',group):
            raise Http403
        title = _("Edit Group")
        edit = True
    else:
        group = None
        if not has_perm(request.user,'user_groups.add_group'):raise Http403
        title = _("Add Group")
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

            EventLog.objects.log(instance=group)

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

        EventLog.objects.log(instance=group)

        group.delete()
        return HttpResponseRedirect(reverse('group.search'))

    (deleted_objects, perms_needed, protected) = get_deleted_objects(
            group, request.user)
    object_name = group.label or group.name

    if perms_needed or protected:
        title = _("Cannot delete %(name)s") % {"name": object_name}
    else:
        title = _("Are you sure?")

    return render_to_response(template_name,
            {'group':group,
             "title": title,
             "object_name": object_name,
             "deleted_objects": deleted_objects,
             "perms_lacking": perms_needed,
             "protected": protected,
             "opts": group._meta,
             },
        context_instance=RequestContext(request))

def group_membership_self_add(request, slug, user_id):
    group = get_object_or_404(Group, slug=slug)
    user = get_object_or_404(User, pk=user_id)

    if not has_view_perm(request.user,'user_groups.view_group', group) and not group.allow_self_add:
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

        if group_membership.is_newsletter_subscribed:
            group_membership.subscribe_to_newsletter()

        EventLog.objects.log(instance=group_membership)

        messages.add_message(request, messages.SUCCESS, _('Successfully added yourself to group %(grp)s' % {'grp':group}))
    else:
        messages.add_message(request, messages.INFO, _('You are already in the group %(grp)s' % {'grp': group}))

    return HttpResponseRedirect(reverse('group.search'))

def group_membership_self_remove(request, slug, user_id):
    group = get_object_or_404(Group, slug=slug)

    if not has_view_perm(request.user,'user_groups.view_group', group) and not group.allow_self_remove:
        raise Http403

    user = get_object_or_404(User, pk=user_id)

    group_membership = GroupMembership.objects.filter(member=user, group=group)

    if group_membership:
        group_membership = group_membership[0]
        if group_membership.member == user:

            EventLog.objects.log(instance=group_membership)
            group_membership.delete()
            messages.add_message(request, messages.SUCCESS, _('Successfully removed yourself from group %(grp)s' % {'grp':group}))
    else:
        messages.add_message(request, messages.INFO, _('You are not in the group %(grp)s' % {'grp': group}))

    return HttpResponseRedirect(reverse('group.search'))

def groupmembership_bulk_add(request, group_slug,
                        form_class=GroupMembershipBulkForm,
                        template_name="user_groups/member_add.html"):
    group = get_object_or_404(Group, slug=group_slug)

    user_count = User.objects.all().count()
    if user_count > 1000:
        return HttpResponseRedirect(reverse('group.adduser_redirect'))

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
                        EventLog.objects.log(instance=old_m)
                        old_m.delete()
            else: #when members is None
                for old_m in old_members:
                    EventLog.objects.log(instance=old_m)
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

                EventLog.objects.log(instance=group_membership)
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

            EventLog.objects.log(instance=group_membership)

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

        EventLog.objects.log(instance=group_membership)
        group_membership.delete()
        messages.add_message(
            request,
            messages.SUCCESS,
            _('Successfully removed %(name)s from group %(grp)s' % {
                'name':user.get_full_name(),
                'grp': group})
        )
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
        title = _('Site Users Added Report')
    elif kind == 'referral':
        event_ids = (125114, 125115)
        title = _('Contacts Report - Referral Analysis Report (all contacts)')
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


@login_required
def group_members_export(request, group_slug, export_target='all'):
    """
    Export members for a specific group
    """
    group = get_object_or_404(Group, slug=group_slug)
    # if they can edit it, they can export it
    if not has_perm(request.user,'user_groups.change_group', group):
        raise Http403

    identifier = '%s_%s' % (int(ttime.time()), request.user.id)
    file_dir = 'export/groups/'
    temp_export_path = '%sgroup_%d_%s_%s_temp.csv' % (file_dir,
                                             group.id,
                                             export_target,
                                            identifier)
    default_storage.save(temp_export_path, ContentFile(''))
    # start the process
    subprocess.Popen(["python", "manage.py",
                  "group_members_export",
                  '--group_id=%d' % group.id,
                  '--export_target=%s' % export_target,
                  '--identifier=%s' % identifier,
                  '--user_id=%s' % request.user.id])
    # log an event
    EventLog.objects.log()
    return redirect(reverse('group.members_export_status',
                     args=[group.slug, export_target, identifier]))


@login_required
def group_members_export_status(request, group_slug,
                            export_target, identifier,
                            template='user_groups/exports/members_export_status.html'):
    if not identifier:
        raise Http404

    group = get_object_or_404(Group, slug=group_slug)
    if not has_perm(request.user,'user_groups.change_group', group):
        raise Http403

    file_dir = 'export/groups/'
    export_path = '%sgroup_%d_%s_%s.csv' % (file_dir,
                                         group.id,
                                         export_target,
                                        identifier)
    download_ready = False
    if default_storage.exists(export_path):
        download_ready = True
    else:
        temp_export_path = '%sgroup_%d_%s_%s_temp.csv' % (
                                        file_dir,
                                        group.id,
                                        export_target,
                                        identifier)
        if not default_storage.exists(temp_export_path) and \
                not default_storage.exists(export_path):
            raise Http404

    # check who will receive the email when the export is done
    # the original user is not necessary the request user
    original_user_id = identifier.split('_')[-1]
    try:
        original_user_id = int(original_user_id)
    except:
        original_user_id = None
    if original_user_id:
        [email_recipient] = User.objects.filter(
                            id=original_user_id
                            ).values_list('email', flat=True
                            ) or [None]
    else:
        email_recipient = None

    context = {'group': group,
               'identifier': identifier,
               'export_target': export_target,
               'download_ready': download_ready,
               'email_recipient': email_recipient}
    return render_to_response(template, context, RequestContext(request))


@login_required
def group_members_export_download(request, group_slug, export_target, identifier):
    if not identifier:
        raise Http404

    group = get_object_or_404(Group, slug=group_slug)
    if not has_perm(request.user,'user_groups.change_group', group):
        raise Http403

    file_dir = 'export/groups/'
    file_name = 'group_%d_%s_%s.csv' % (group.id, export_target, identifier)
    export_path = '%s%s' % (file_dir, file_name)
    if not default_storage.exists(export_path):
        raise Http404

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=membership_export_%s' % file_name
    response.content = default_storage.open(export_path).read()
    return response


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
    from tendenci.apps.forms_builder.forms.models import FieldEntry

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
    from tendenci.apps.forms_builder.forms.models import FieldEntry

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

def group_subscriber_import(request, group_slug, template="user_groups/import_subscribers.html"):
    """
    Import subscribers for a specific group
    """
    raise Http404

    # form_class=UploadForm
    # group = get_object_or_404(Group, slug=group_slug)

    # # if they can edit, they can export
    # if not has_perm(request.user,'user_groups.change_group', group):
    #     raise Http403

    # if request.method == 'POST':
    #     form = form_class(request.POST, request.FILES)
    #     if form.is_valid():
    #         csv = form.save(commit=False)
    #         csv.group = group
    #         csv.creator = request.user
    #         csv.creator_username = request.user.username
    #         csv.owner = request.user
    #         csv.owner_username = request.user.username
    #         csv.save()

    #         if not settings.CELERY_IS_ACTIVE:
    #             # if celery server is not present
    #             # evaluate the result and render the results page
    #             result = ImportSubscribersTask()
    #             subs = result.run(group, csv.file.path)
    #             return render_to_response('user_groups/import_subscribers_result.html', {
    #                 'group':group,
    #                 'subs':subs,
    #             }, context_instance=RequestContext(request))
    #         else:
    #             result = ImportSubscribersTask.delay(group, csv.file.path)
    #             return redirect('subscribers_import_status', group.slug, result.task_id)
    # else:
    #     form = form_class()

    # return render_to_response(template, {
    #     'group':group,
    #     'form':form,
    # }, context_instance=RequestContext(request))

@login_required
def subscribers_import_status(request, group_slug, task_id, template_name='user_groups/import_status.html'):
    """
    Checks if a subscriber import is completed.
    """
    group = get_object_or_404(Group, slug=group_slug)

    if not request.user.profile.is_superuser:
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

@login_required
def groupmembership_bulk_add_redirect(request, template_name='user_groups/bulk_add_redirect.html'):
    EventLog.objects.log()

    return render_to_response(template_name, {}, context_instance=RequestContext(request))


@login_required
def import_add(request, form_class=ImportForm,
                template_name="user_groups/imports/user_groups_add.html"):
    """Event Import Step 1: Validates and saves import file"""
    if not request.user.profile.is_superuser:
        raise Http403

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            import_i = form.save(commit=False)
            import_i.app_label = 'events'
            import_i.model_name = 'event'
            import_i.save()

            EventLog.objects.log()

            # reset the password_promt session
            del request.session['password_promt']

            return HttpResponseRedirect(
                reverse('group.import_preview', args=[import_i.id]))
    else:
        form = form_class()
    return render_to_response(template_name, {'form': form},
        context_instance=RequestContext(request))

@login_required
def import_preview(request, import_id,
                    template_name="user_groups/imports/user_groups_preview.html"):
    if not request.user.profile.is_superuser:
        raise Http403

    import_i = get_object_or_404(Import, id=import_id)

    user_groups_list, invalid_list = user_groups_import_process(import_i,
                                                        preview=True)

    return render_to_response(template_name, {
        'total': import_i.total_created + import_i.total_invalid,
        'user_groups_list': user_groups_list,
        'import_i': import_i,
    }, context_instance=RequestContext(request))

@login_required
def import_process(request, import_id,
                template_name="user_groups/imports/user_groups_process.html"):
    """Import Step 3: Import into database"""

    if not request.user.profile.is_superuser:
        raise Http403   # admin only page

    import_i = get_object_or_404(Import, id=import_id)

    subprocess.Popen(['python', 'manage.py', 'import_groups', str(import_id)])

    return render_to_response(template_name, {
        'total': import_i.total_created + import_i.total_invalid,
        "import_i": import_i,
    }, context_instance=RequestContext(request))

@login_required
def import_download_template(request, file_ext='.csv'):
    if not request.user.profile.is_superuser:
        raise Http403

    if file_ext == '.csv':
        filename = "import-user-groups.csv"
    else:
        filename = "import-user-groups.xls"

    import_field_list = ['name', 'label', 'type',
                         'email_recipient', 'description',
                          'auto_respond_priority', 'notes']
    data_row_list = []

    return render_excel(filename, import_field_list, data_row_list, file_ext)


# Newsletter stuff here:
@login_required
def subscribe_to_newsletter_interactive(request, group_slug):
    group = get_object_or_404(Group, slug=group_slug)

    groupmembership = get_object_or_404(GroupMembership,
                        group=group,
                        member=request.user,
                        status=True,
                        status_detail='active')

    if groupmembership.subscribe_to_newsletter():
        messages.success(request, _('Successfully subscribed to Newsletters.'))

    return redirect(reverse('group.detail', kwargs={'group_slug': group_slug}))


@login_required
def unsubscribe_to_newsletter_interactive(request, group_slug):
    group = get_object_or_404(Group, slug=group_slug)

    groupmembership = get_object_or_404(GroupMembership,
                        group=group,
                        member=request.user,
                        status=True,
                        status_detail='active')

    if groupmembership.unsubscribe_to_newsletter():
        messages.success(request, _('Successfully unsubscribed to Newsletters.'))

    return redirect(reverse('group.detail', kwargs={'group_slug': group_slug}))


def subscribe_to_newsletter_noninteractive(request, group_slug):
    pass


def unsubscribe_to_newsletter_noninteractive(request, group_slug, newsletter_key):
    group = get_object_or_404(Group, slug=group_slug)

    groupmembership = get_object_or_404(GroupMembership,
                        group=group,
                        status=True,
                        status_detail='active',
                        newsletter_key=newsletter_key)
    if not groupmembership.unsubscribe_to_newsletter():
        raise Http404

    return render(request, 'user_groups/newsletter_unsubscribe.html')

