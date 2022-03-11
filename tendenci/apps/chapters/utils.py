from datetime import datetime, date, timedelta, time
import dateutil.parser as dparser
from decimal import Decimal

from django.core import exceptions
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.template import Context, Template
from django.template.loader import get_template
from django.urls.base import reverse

from tendenci.apps.chapters.models import (
        Chapter, ChapterMembershipApp,
        ChapterMembership, ChapterMembershipType)
from tendenci.apps.user_groups.models import Group
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.shortcuts import _strip_content_above_doctype
from tendenci.apps.newsletters.utils import get_newsletter_connection, is_newsletter_relay_set


def get_newsletter_group_queryset():
    groups_qs = Group.objects.filter(status_detail="active",
                                     allow_self_add=True,
                                    ).order_by('name')
    if Chapter.objects.exists():
        groups_qs = groups_qs.exclude(id__in=Chapter.objects.values_list('group', flat=True))

    return groups_qs


def get_chapter_membership_field_values(chapter_membership, app_fields):
    """
    Get a list of chapter membership field values corresponding to the app_fields.
    """
    data = []
    user = chapter_membership.user
    if hasattr(user, 'profile'):
        profile = user.profile
    else:
        profile = None
    
    for field in app_fields:
        field_name = field.field_name
        value = ''
        if hasattr(user, field_name):
            value = getattr(user, field_name)
        elif hasattr(profile, field_name):
            value = getattr(profile, field_name)
        elif hasattr(chapter_membership, field_name):
            value = getattr(chapter_membership, field_name)
        data.append(value)
    return data


def get_notice_token_help_text(notice=None):
    """Get the help text for how to add the token in the email content,
        and display a list of available token.
    """
    help_text = ''
    app = ChapterMembershipApp.objects.current_app()

    # render the tokens
    help_text += '<div>'
    help_text += """
                <div style="margin-bottom: 1em;">
                You can use tokens to display chapter member info or site specific
                information.
                A token is a field name wrapped in
                {{ }} or [ ]. <br />
                For example, token for first_name field: {{ first_name }}.
                Please note that tokens for chapter member number, chapter membership link,
                and expiration date/time are not available until the chapter membership
                is approved.
                </div>
                """

    help_text += '<div id="toggle_token_view"><a href="javascript:;">' + \
                'Click to view available tokens</a></div>'
    help_text += '<div id="notice_token_list">'
    if app:
        help_text += f'<div style="font-weight: bold;">Field Tokens</div>'
        fields = app.fields.filter(display=True).exclude(field_name=''
                                                         ).order_by('position')

        help_text += "<ul>"
        for field in fields:
            help_text += f'<li>{{ {field.field_name} }} - (for {field.label})</li>'
        help_text += "</ul>"
    else:
        help_text += '<div>No field tokens because there is no ' + \
                    'applications.</div>'

    other_labels = [
                    'chapter_name',
                    'first_name',
                    'last_name',
                    'email',
                    'username',
                    'member_number',
                    'membership_type',
                    'membership_price',
                    'total_amount',
                    'view_link',
                    'edit_link',
                    'invoice_link',
                    'renew_link',
                    'expire_dt',]

    other_labels += ['site_contact_name',
                    'site_contact_email',
                    'site_display_name',
                    'time_submitted',
                    ]

    help_text += '<div style="font-weight: bold;">Non-field Tokens</div>'
    help_text += "<ul>"
    for label in other_labels:
        help_text += '<li>{{ %s }}</li>' % label
    help_text += "</ul>"
    help_text += "</div>"
    help_text += "</div>"

    help_text += """
                <script>
                    (function($) {
                        $(document).ready(function() {
                            $('#notice_token_list').hide();
                                 $('#toggle_token_view').click(function () {
                                $('#notice_token_list').toggle();
                            });
                        });
                    }(jQuery));
                </script>
                """

    return help_text


def email_chapter_members(email, chapter_memberships, **kwargs):
    """
    Email to pending members or corporate members.
    """
    site_url = get_setting('site', 'global', 'siteurl')
    site_display_name = get_setting('site', 'global', 'sitedisplayname')
    tmp_body = email.body
    
    # if possible, use the email backend set up for newsletters
    if is_newsletter_relay_set():
        connection = get_newsletter_connection()
    else:
        connection = None

    request = kwargs.get('request')
    total_sent = 0
    subject = email.subject
    
    msg = '<div class="hide" id="m-streaming-content" style="margin: 2em 5em;text-align: left; line-height: 1.3em;">'
    msg += '<h1>Processing ...</h1>'

    for member in chapter_memberships:
        first_name = member.user.first_name
        last_name = member.user.last_name

        email.recipient = member.user.email

        if email.recipient:
            view_url = '{0}{1}'.format(site_url, reverse('chapters.membership_details', args=[member.id]))
            edit_url = '{0}{1}'.format(site_url, reverse('chapters.membership_edit', args=[member.id]))
            template = Template(email.body)
            context = Context({'site_url': site_url,
                               'site_display_name': site_display_name,
                               "first_name": first_name,
                               'last_name': last_name,
                               'view_url': view_url,
                               'edit_url': edit_url,
                               'chapter_name': member.chapter.title})
            email.body = template.render(context)
            
            # replace relative to absolute urls
            email.body = email.body.replace("src=\"/", f"src=\"{site_url}/")
            email.body = email.body.replace("href=\"/", f"href=\"{site_url}/")

            email.send(connection)
            total_sent += 1

            msg += f'{total_sent}. Email sent to {first_name} {last_name} {email.recipient}<br />'

            if total_sent % 10 == 0:
                yield msg
                msg = ''

        email.body = tmp_body  # restore to the original

    request.session['email_subject'] = email.subject
    request.session['email_body'] = email.body

    dest = _('Chapter members')

    opts = {}
    opts['summary'] = '<font face=""Arial"" color=""#000000"">'
    opts['summary'] += 'Emails sent to {0} ({1})</font><br><br>'.format(dest, total_sent)
    opts['summary'] += '<font face=""Arial"" color=""#000000"">'
    opts['summary'] += 'Email Sent Appears Below in Raw Format'
    opts['summary'] += '</font><br><br>'
    opts['summary'] += email.body

    # send summary
    email.subject = 'SUMMARY: %s' % email.subject
    email.body = opts['summary']
    email.recipient = request.user.email
    email.send(connection)

    msg += f'DONE!<br /><br />Successfully sent email "{subject}" to <strong>{total_sent}</strong> pending members.'
    msg += '</div>'
    yield msg
    
    template_name='chapters/memberships/message/email-chapter-members-conf.html'
    template = get_template(template_name)
    context={'total_sent': total_sent,
             'chapter_memberships': chapter_memberships}
    rendered = template.render(context=context, request=request)
    rendered = _strip_content_above_doctype(rendered)
    yield rendered


class ImportChapterMembership(object):
    """
    Check and process (insert/update) a chapter membership.
    """
    def __init__(self, request_user, mimport,
                               dry_run=True, **kwargs):
        """
        :param mimport: a instance of ChapterMembershipImport
        :param dry_run: if True, do everything except updating the database.
        """
        self.key = mimport.key
        self.request_user = request_user
        self.mimport = mimport
        self.dry_run = dry_run
        self.summary_d = self.init_summary()
        self.chapter_membership_fields = dict([(field.name, field)
                            for field in ChapterMembership._meta.fields
                            if field.get_internal_type() != 'AutoField' and
                            field.name not in ['user', 'membership_type', 'chapter', 'guid']])
        self.private_settings = self.set_default_private_settings()
        # all chapter membership types
        self.all_membership_type_ids = ChapterMembershipType.objects.values_list(
                                        'id', flat=True)
        self.default_membership_type_id = self.all_membership_type_ids and self.all_membership_type_ids[0]

        self.app = ChapterMembershipApp.objects.current_app()


    def init_summary(self):
        return {
                 'insert': 0,
                 'update': 0,
                 'update_insert': 0,
                 'invalid': 0
                 }

    def set_default_private_settings(self):
        # public, private, all-members, member-type
        memberprotection = get_setting('module',
                                       'memberships',
                                       'memberprotection')
        d = {'allow_anonymous_view': False,
             'allow_user_view': False,
             'allow_member_view': False,
             'allow_user_edit': False,
             'allow_member_edit': False}

        if memberprotection == 'public':
            d['allow_anonymous_view'] = True
        if memberprotection == 'all-members':
            d['allow_user_view'] = True
        if memberprotection == 'member-type':
            d['allow_member_view'] = True
        return d

    def clean_membership_type_id(self, memb_data, **kwargs):
        """
        Ensure we have a valid membership type.
        """
        if 'membership_type_id' in memb_data and memb_data['membership_type_id']:
            value = memb_data['membership_type_id']

            if str(value).isdigit():
                value = int(value)
                if value not in self.all_membership_type_ids:
                    return False, _(f'Invalid membership type id "{value}"')
                else:
                    memb_data['membership_type_id'] = value
            else:
                if not ChapterMembershipType.objects.filter(
                                            name=value).exists():
                    return False, _(f'Invalid membership type id "{value}"')
                else:
                    memb_data['membership_type_id'] = ChapterMembershipType.objects.filter(
                                                        name=value
                                                        ).values_list(
                                                            'id', flat=True)[0]
        else:
            # the spread sheet doesn't have the membership_type_id field,
            # assign the default one
            if self.default_membership_type_id:
                memb_data['membership_type_id'] = self.default_membership_type_id
            else:
                return False, _('No membership type. Please add one to the site.')

        return True, ''

    def clean_username(self, memb_data, **kwargs):
        """
        Ensure we have a valid username.
        """
        username = memb_data.get('username')
        if not username:
            return False, _('username not specified.')
        if not User.objects.filter(username=username).exists():
            return False, _('username does not exist.')
        return True, ''

    def clean_chapter_id(self, memb_data, **kwargs):
        """
        Ensure we have a valid username.
        """
        chapter_id = memb_data.get('chapter_id')
        if not chapter_id:
            return False, _('chapter_id not specified.')
        if not Chapter.objects.filter(id=chapter_id).exists():
            return False, _('chapter_id does not exist.')
        return True, ''

    def check_missing_fields(self, memb_data, **kwargs):
        """
        Check if we have enough data to process for this row.
        """
        missing_field_msg = ''
        is_valid = True

        if self.key == 'username,membership_type_id,chapter_id':
            missing_items = []
            if not memb_data['username']:
                missing_items.append('username')
            if not memb_data['membership_type_id']:
                missing_items.append('membership_type_id')
            if not memb_data['chapter_id']:
                missing_items.append('chapter_id')
            if missing_items:
                if len(missing_items) == 1:
                    missing_field_msg = f"Missing key '{missing_items[0]}'"
                else:
                    missing_items_str = ', '.join(missing_items)
                    missing_field_msg = f"Missing keys '{missing_items_str}'"
    
        if missing_field_msg:
            is_valid = False
    
        return is_valid, missing_field_msg

    def process_chapter_membership(self, idata, **kwargs):
        """
        Check if it's insert or update. If dry_run is False,
        do the import to the chapter_membership.

        :param idata: an instance of ChapterMembershipImportData
        """
        self.memb_data = idata.row_data
        user_display = {
            'error': '',
            'user': None,
            'action': ''
        }

        is_valid, error_msg = self.check_missing_fields(self.memb_data)
        if is_valid:
            is_valid, error_msg = self.clean_membership_type_id(self.memb_data)
        if is_valid:
            is_valid, error_msg = self.clean_username(self.memb_data)
        if is_valid and not self.mimport.chapter:
            is_valid, error_msg = self.clean_chapter_id(self.memb_data)

        # don't process if we have missing value of required fields
        if not is_valid:
            user_display['error'] = error_msg
            user_display['action'] = 'skip'
            if not self.dry_run:
                self.summary_d['invalid'] += 1
                idata.action_taken = 'skipped'
                idata.error = user_display['error']
                idata.save()
        else:
            user = User.objects.get(username=self.memb_data.get('username'))

            # pick the most recent one
            chapter_memb = None
            chapter_memberships = ChapterMembership.objects.filter(
                                    user=user,
                                    membership_type__id=self.memb_data['membership_type_id'],
                                    ).exclude(
                                      status_detail='archive')
            if self.mimport.chapter:
                chapter_memberships = chapter_memberships.filter(chapter_id=self.mimport.chapter.id)
            else:
                chapter_memberships = chapter_memberships.filter(chapter_id=self.memb_data['chapter_id'])
            if chapter_memberships.exists():
                [chapter_memb] = chapter_memberships.order_by('-id')[:1] or [None]

            if not chapter_memb:
                user_display['memb_action'] = 'insert'
                user_display['action'] = 'inseart'
            else:
                user_display['memb_action'] = 'update'
                user_display['action'] = 'update'

            if not self.dry_run:
                if user_display['memb_action'] == 'insert':
                    self.summary_d['insert'] += 1
                    idata.action_taken = 'insert'
                else:
                    self.summary_d['update'] += 1
                    idata.action_taken = 'update'

                self.field_names = self.memb_data
                # now do the update or insert
                self.do_import_chapter_membership(user, self.memb_data, chapter_memb, user_display)
                idata.save()
                return

        user_display.update({
            'username': self.memb_data.get('username', ''),
            'membership_type_id': self.memb_data.get('membership_type_id', ''),
            'chapter_id': self.memb_data.get('chapter_id', ''),
        })

        return user_display

    def do_import_chapter_membership(self, user, memb_data, chapter_memb, action_info):
        """
        Database import here - insert or update
        """
        # membership
        if not chapter_memb:
            if self.mimport.chapter:
                chapter_id = self.mimport.chapter.id
            else:
                chapter_id = memb_data.get('chapter_id')
            chapter_memb = ChapterMembership(
                user=user,
                membership_type_id=memb_data.get('membership_type_id'),
                chapter_id=chapter_id,
                app=self.app)
            chapter_memb.save()

        self.assign_import_values_from_dict(chapter_memb, action_info['memb_action'])
        if not chapter_memb.creator:
            chapter_memb.creator = self.request_user
        if not chapter_memb.creator_username:
            chapter_memb.creator_username = self.request_user.username
        if not chapter_memb.owner:
            chapter_memb.owner = self.request_user
        if not chapter_memb.owner_username:
            chapter_memb.owner_username = self.request_user.username

        # Set status to True
        # The False status means DELETED - It would defeat the purpose of import
        chapter_memb.status = True

        if not chapter_memb.status_detail:
            chapter_memb.status_detail = 'active'
        else:
            chapter_memb.status_detail = chapter_memb.status_detail.lower()
            if chapter_memb.status_detail not in ['active', 'pending', 'expired', 'archive', 'disapproved']:
                chapter_memb.status_detail = 'active'

        # membership type
        if not hasattr(chapter_memb, "membership_type") or not chapter_memb.membership_type:
            # last resort - use the default membership type
            chapter_memb.membership_type_id = self.default_membership_type_id

        # no join_dt - set one
        if not hasattr(chapter_memb, 'join_dt') or not chapter_memb.join_dt:
            if chapter_memb.status and chapter_memb.status_detail == 'active':
                chapter_memb.join_dt = datetime.now()

        # no approved_dt - set one
        if not hasattr(chapter_memb, 'approved_dt') or not chapter_memb.approved_dt:
            if chapter_memb.status and chapter_memb.status_detail == 'active':
                chapter_memb.approved = True
                chapter_memb.approved_dt = chapter_memb.join_dt
                chapter_memb.approved_denied_dt = chapter_memb.join_dt

        # no expire_dt - get it via membership_type
        if not hasattr(chapter_memb, 'expire_dt') or not chapter_memb.expire_dt:
            if chapter_memb.membership_type:
                expire_dt = chapter_memb.membership_type.get_expiration_dt(
                                            join_dt=chapter_memb.join_dt)
                setattr(chapter_memb, 'expire_dt', expire_dt)

        chapter_memb.save()

        if not chapter_memb.entity:
            chapter_memb.entity = chapter_memb.chapter.entity
            chapter_memb.save()

        # member_number
        if not chapter_memb.member_number:
            if chapter_memb.is_active():
                chapter_memb.member_number = chapter_memb.set_member_number()
                chapter_memb.save()

        # add to group only for the active memberships
        if chapter_memb.is_active():
            chapter_memb.group_refresh()

    def assign_import_values_from_dict(self, instance, action):
        """
        Assign the import value from a dictionary object
        - self.memb_data.
        """
        assign_to_fields =self.chapter_membership_fields

        for field_name in self.field_names:
            if field_name in assign_to_fields:
                if any([
                        action == 'insert',
                        self.mimport.override,
                        not hasattr(instance, field_name) or
                        getattr(instance, field_name) == '' or
                        getattr(instance, field_name) is None
                        ]):
                    value = self.memb_data[field_name]
                    value = self.clean_data(value, assign_to_fields[field_name])

                    setattr(instance, field_name, value)

        # if insert, set defaults for the fields not in csv.
        for field_name in assign_to_fields:
            if field_name not in self.field_names and action == 'insert':
                if field_name not in self.private_settings:
                    value = self.get_default_value(assign_to_fields[field_name])

                    if value is not None:
                        setattr(instance, field_name, getattr(instance, field_name) or value)

    def get_default_value(self, field):
        # if allows null or has default, return None
        if field.null or field.has_default():
            return None

        field_type = field.get_internal_type()

        if field_type in ['BooleanField', 'NullBooleanField']:
            return False

        if field_type == 'DateField':
            return date

        if field_type == 'DateTimeField':
            return datetime.now()

        if field_type == 'DecimalField':
            return Decimal(0)

        if field_type == 'IntegerField':
            return 0

        if field_type == 'FloatField':
            return 0

        if field_type == 'ForeignKey':
            try:
                model = field.remote_field.parent_model()
            except AttributeError:
                model = field.remote_field.model
            [value] = model.objects.all()[:1] or [None]
            return value

        return ''

    def clean_data(self, value, field):
        """
        Clean the data based on the field type.
        """
        field_type = field.get_internal_type()
        if field_type in ['CharField', 'EmailField',
                          'URLField', 'SlugField']:
            if not value:
                value = ''
            if len(value) > field.max_length:
                # truncate the value to ensure its length <= max_length
                value = value[:field.max_length]
            try:
                value = field.to_python(value)
            except exceptions.ValidationError:
                if field.has_default():
                    value = field.get_default()
                else:
                    value = ''

        elif field_type in ['BooleanField', 'NullBooleanField']:
            try:
                if value in [True, 1, 'TRUE']:
                    value = True
                value = field.to_python(value)
            except exceptions.ValidationError:
                value = False
        elif field_type == 'DateField':
            if value:
                value = dparser.parse(value)
                try:
                    value = field.to_python(value)
                except exceptions.ValidationError:
                    pass

            if not value:
                if not field.null:
                    value = date

        elif field_type == 'DateTimeField':
            if value:
                value = dparser.parse(value)
                try:
                    value = field.to_python(value)
                except exceptions.ValidationError:
                    pass

            if not value:
                if value == '':
                    value = None
                if not field.null:
                    value = datetime.now()
        elif field_type == 'DecimalField':
            try:
                value = field.to_python(value)
            except exceptions.ValidationError:
                value = Decimal(0)
        elif field_type == 'IntegerField':
            try:
                value = int(value)
            except:
                value = 0
        elif field_type == 'FloatField':
            try:
                value = float(value)
            except:
                value = 0
        elif field_type == 'ForeignKey':
            # assume id for foreign key
            try:
                value = int(value)
            except:
                value = None

            if value:
                try:
                    model = field.remote_field.parent_model()
                except AttributeError:
                    model = field.remote_field.model
                [value] = model.objects.filter(pk=value)[:1] or [None]

            if not value and not field.null:
                # if the field doesn't allow null, grab the first one.
                try:
                    model = field.remote_field.parent_model()
                except AttributeError:
                    model = field.remote_field.model
                [value] = model.objects.all().order_by('id')[:1] or [None]

        return value
