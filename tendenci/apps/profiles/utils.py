from builtins import str
import re
import time as ttime
from datetime import datetime, date, time
from string import digits
from random import choice
from decimal import Decimal
import dateutil.parser as dparser
import pytz
import csv

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.urls import reverse
from django.db.models import Q
from django.db.models.fields import AutoField
from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.utils.html import format_html
from django.core import exceptions

from tendenci.apps.profiles.models import Profile
from tendenci.apps.user_groups.models import GroupMembership, Group
from tendenci.apps.base.utils import UnicodeWriter, normalize_newline
from tendenci.apps.emails.models import Email
from tendenci.apps.perms.utils import get_query_filters
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.utils import escape_csv


def profile_edit_admin_notify(request, old_user, old_profile, profile, **kwargs):

    subject = 'User Account Modification Notice for %s' % get_setting('site', 'global', 'sitedisplayname')
    body = render_to_string(template_name='profiles/edit_notice.txt',
                               context={'old_user':old_user,
                                'old_profile': old_profile,
                                'profile': profile},
                               request=request)

    sender = settings.DEFAULT_FROM_EMAIL
    recipients = ['%s<%s>' % (r[0], r[1]) for r in settings.ADMINS]
    email = Email(
            sender=sender,
            recipient=recipients,
            subject=subject,
            body=body)
    email.send(fail_silently=True)


# return admin auth group as a list
def get_admin_auth_group(name="Admin"):
    from django.contrib.auth.models import Group as Auth_Group

    try:
        auth_group = Auth_Group.objects.get(name=name)
    except Auth_Group.DoesNotExist:
        auth_group = Auth_Group(name=name)
        auth_group.save()

    return auth_group


def get_groups(user, filter=None):
    """
    Returns the groups of a given user.
    if filter is given it will filter the user's groups based on it.
    filter is assumed to be a QuerySet or a SearchQuerySet of Group.
    """
    memberships = GroupMembership.objects.filter(member=user)

    if filter:
        pks = [group.pk for group in filter]
        memberships = memberships.filter(group__pk__in = pks)

    groups = []
    for member in memberships:
        groups.append(member.group)

    return groups

def get_memberships(user, filter=None):
    """
    Returns the memberships of a given user.
    if filter is given it will filter the user's memberships based on it.
    filter is assumed to be a QuerySet or a SearchQuerySet of Group.
    """
    memberships = GroupMembership.objects.filter(member=user)

    if filter:
        pks = [group.pk for group in filter]
        memberships = memberships.filter(group__pk__in = pks)

    return memberships

def group_choices(user):
    """
    returns a list of (group.pk, group.label) for groups viewable
    for the given user.
    """

    filters = get_query_filters(user, 'groups.view_group', perms_field=False)
    groups = Group.objects.filter(filters).exclude(type="membership").distinct()

    if not user.profile.is_superuser:
        groups = groups.exclude(allow_self_add=False)

    choices = [(group.pk, "%s (%s)" % (group.label, group.name)) for group in groups]

    return choices


def update_user(user, **kwargs):
    for k, v in kwargs.items():
        if hasattr(user, k):
            setattr(user, k, v)
    user.save()


def make_username_unique(un):
    """
    Requires a string parameter.
    Returns a unique username by appending
    a digit to the end of the username.
    """
    others = []  # find similiar usernames
    for u in User.objects.filter(username__startswith=un):
        if u.username.replace(un, '0').isdigit():
            others.append(int(u.username.replace(un, '0')))

    if others and 0 in others:
        # the appended digit will compromise the username length
        un = '%s%s' % (un, str(max(others) + 1))

    return un


def spawn_username(fn=u'', ln=u'', em=u''):
    """
    Uses a first name, last name and email to
    spawn a typical username.  All usernames are
    lowercase.  All usernames are unique.

    Usernames generated via first or last name will only
    contain letters, digits, and periods.

    Usernames generated via the email address may contain
    letters, digits, underscores, hypens, periods and at-symbols

    Usernames that 100% auto-generated start with 'user.' and end
    with 10 digits which can later be replaced by the user primary key.
    Example user.3482938481
    """

    django_max_un_length = 150
    max_length = django_max_un_length - 3  # to account for appended numbers

    # only letters and digits
    fn = re.sub(r'[^A-Za-z0-9]', '', fn)
    ln = re.sub(r'[^A-Za-z0-9]', '', ln)

    # only letters digits underscores dashes @ + .
    em = re.sub(r'[^\w@+.-]', '', em)
    
    if em:
        return make_username_unique(em[:max_length].lower())

    if fn and ln:
        un = '%s.%s' % (fn, ln)
        return make_username_unique(un[:max_length].lower())

    if fn:
        return make_username_unique(fn[:max_length].lower())

    if ln:
        return make_username_unique(ln[:max_length].lower())


    int_string = ''.join([choice(digits) for x in range(10)])
    return 'user.%s' % int_string


def get_member_reminders(user, view_self=False):
    active_qs = Q(status_detail__iexact='active')
    expired_qs = Q(status_detail__iexact='expired')

    memberships = user.membershipdefault_set.filter(
        status=True) & user.membershipdefault_set.filter(
            active_qs | expired_qs).order_by('expire_dt')
    count = len(memberships)

    reminders = ()
    for membership in memberships:
        # renew_link depends on membership.app
        if not membership.app:
            membership.get_app()

        if count > 1:
            my_msg = 'Your membership for %s' % membership.membership_type.name
        else:
            my_msg = 'Your membership'

        renew_link = u''
        if hasattr(membership, 'app') and membership.app:
            renew_link = '%s%s?username=%s&membership_type_id=%s' % (
                get_setting('site', 'global', 'siteurl'),
                reverse('membership_default.renew',
                        kwargs={'slug': membership.app.slug,
                                'membership_id': membership.id}),
                membership.user.username,
                membership.membership_type.pk)

        if membership.in_grace_period() or membership.is_expired():
            if membership.can_renew():
                # expired but can renew
                message = format_html(
                    '{} has expired. <a href="{}">Renew Now</a> to remain an active member!',
                    my_msg, renew_link)
                reminders += ((message, renew_link, 'Renew Now'),)
            else:
                # expired and out of renewal period
                message = format_html('{} has expired.', my_msg)
                reminders += ((message, renew_link, 'Re-register as a member here'),)
        else:
            # not expired, but in renewal period
            if membership.can_renew():
                message = format_html(
                    '{} will expire on {}. <a href="{}">Renew Now</a> to remain an active member!',
                    my_msg, membership.expire_dt.strftime('%d-%b-%Y'), renew_link)
                reminders += ((message, renew_link, 'Renew Here'),)

    return reminders


def clean_username(username):
    """
    Removes improper characters from a username
    """
    bad_characters = " !#$%^&*()[]'\""

    for char in bad_characters:
        if char in username:
            username = username.replace(char, '')

    return username


def process_export(export_fields='all_fields', identifier=u'', user_id=0):
    from tendenci.apps.perms.models import TendenciBaseModel

    if export_fields == 'main_fields':
        user_field_list = [
            'username',
            'first_name',
            'last_name',
            'email']

        profile_field_list = [
            'salutation',
            'initials',
            'display_name',
            'company',
            'department',
            'position_title',
            'sex',
            'address',
            'address2',
            'city',
            'state',
            'zipcode',
            'country',
            'region',
            'phone',
            'phone2',
            'fax',
            'work_phone',
            'home_phone',
            'mobile_phone',
            'url',
            'url2',
            'dob',
            'status_detail']
    else:
        # base ------------
        base_field_list = [
            smart_str(field.name) for field in TendenciBaseModel._meta.fields
            if not field.__class__ == AutoField]

        # user ------------
        user_field_list = [
            smart_str(field.name) for field in User._meta.fields
            if not field.__class__ == AutoField]
        user_field_list.remove('password')

        # profile ---------
        profile_field_list = [
            smart_str(field.name) for field in Profile._meta.fields
            if not field.__class__ == AutoField]
        profile_field_list = [
            name for name in profile_field_list
            if name not in base_field_list]
        profile_field_list.remove('guid')
        profile_field_list.remove('user')
        # append base fields at the end

    field_list = user_field_list + profile_field_list

    identifier = identifier or int(ttime.time())
    file_name_temp = 'export/profiles/%s_temp.csv' % identifier

    with default_storage.open(file_name_temp, 'w') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=field_list)
        csv_writer.writeheader()

        profiles = Profile.objects.all()
        for profile in profiles:
            p_user = profile.user
            row_dict = {}
            for field_name in field_list:
                if field_name in profile_field_list:
                    item = getattr(profile, field_name)
                elif field_name in user_field_list:
                    item = getattr(p_user, field_name)
                else:
                    item = ''
                if item:
                    if isinstance(item, datetime):
                        item = item.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(item, date):
                        item = item.strftime('%Y-%m-%d')
                    elif isinstance(item, time):
                        item = item.strftime('%H:%M:%S')
                    elif isinstance(item, str):
                        item = escape_csv(item)
                row_dict[field_name] = item
            csv_writer.writerow(row_dict)

    # rename the file name
    file_name = 'export/profiles/%s.csv' % identifier
    default_storage.save(file_name, default_storage.open(file_name_temp, 'rb'))

    # delete the temp file
    default_storage.delete(file_name_temp)

    # notify user that export is ready to download
    [user] = User.objects.filter(pk=user_id)[:1] or [None]
    if user and user.email:
        download_url = reverse('profile.export_download', args=[identifier])

        site_url = get_setting('site', 'global', 'siteurl')
        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        parms = {
            'download_url': download_url,
            'user': user,
            'site_url': site_url,
            'site_display_name': site_display_name,
            'export_fields': export_fields}

        subject = render_to_string(
            template_name='profiles/notices/export_ready_subject.html', context=parms)
        subject = subject.strip('\n').strip('\r')

        body = render_to_string(
            template_name='profiles/notices/export_ready_body.html', context=parms)

        email = Email(
            recipient=user.email,
            subject=subject,
            body=body)
        email.send()


def check_missing_fields(user_data, key, **kwargs):
    """
    Check if we have enough data to process for this row.
    """
    missing_field_msg = ''
    is_valid = True
    if key in ['first_name,last_name,email']:
        if not any([user_data['email'],
                    user_data['first_name'],
                    user_data['last_name']]):
            missing_field_msg = "Missing key(s) 'email' or " + \
                                "('first name' or 'last name')"
    elif key in ['first_name,last_name,phone']:
        if not any([user_data['phone'],
                    user_data['first_name'],
                    user_data['last_name']]):
            missing_field_msg = "Missing key(s) 'phone' or " + \
                                "('first name' or 'last name')"
    elif key in ['first_name,last_name,company']:
        if not any([user_data['company'],
                    user_data['first_name'],
                    user_data['last_name']]):
            missing_field_msg = "Missing key(s) 'company' or " + \
                                "('first name' or 'last name')"
    elif key == 'email':
        if not user_data['email']:
            missing_field_msg = "Missing key 'email'"
    elif key == 'username':
        if not user_data['username']:
            missing_field_msg = "Missing key 'username'"
    else:
        is_valid = False
        missing_field_msg = "No key specified"

    if missing_field_msg:
        is_valid = False

    return is_valid, missing_field_msg


def get_user_by_email(email):
    """
    Get user by email address.
    """
    if not email:
        return None

    return User.objects.filter(email__iexact=email).order_by(
                    '-is_active', '-is_superuser', '-is_staff')


def get_user_by_fn_ln_email(first_name, last_name, email):
    """
    Get user by first name, last name and email.
    """
    if not any([first_name, last_name, email]):
        return None

    return User.objects.filter(first_name__iexact=first_name,
                                last_name__iexact=last_name,
                                email__iexact=email).order_by(
                    '-is_active', '-is_superuser', '-is_staff')


def get_user_by_fn_ln_phone(first_name, last_name, phone):
    """
    Get user by first name, last name and phone.
    """
    if not any([first_name, last_name, phone]):
        return None

    profiles = Profile.objects.filter(
                user__first_name__iexact=first_name,
                user__last_name__iexact=last_name,
                phone__iexact=phone).order_by(
                    '-user__is_active',
                    '-user__is_superuser',
                    '-user__is_staff')
    if profiles:
        return [profile.user for profile in profiles]
    return None

def get_user_by_fn_ln_company(first_name, last_name, company):
    """
    Get user by first name, last name and email.
    """
    if not any([first_name, last_name, company]):
        return None

    profiles = Profile.objects.filter(
                user__first_name__iexact=first_name,
                user__last_name__iexact=last_name,
                company__iexact=company).order_by(
                    '-user__is_active',
                    '-user__is_superuser',
                    '-user__is_staff'
                        )
    if profiles:
        return [profile.user for profile in profiles]
    return None


class ImportUsers(object):
    """
    Check and process (insert/update) a user.
    """
    def __init__(self, request_user, uimport,
                               dry_run=True, **kwargs):
        """
        :param uimport: a instance of UserImport
        :param dry_run: if True, do everything except updating the database.
        """
        self.key = uimport.key
        self.request_user = request_user
        self.uimport = uimport
        self.dry_run = dry_run
        self.summary_d = self.init_summary()
        self.user_fields = dict([(field.name, field)
                            for field in User._meta.fields
                            if field.get_internal_type() != 'AutoField'])
        self.profile_fields = dict([(field.name, field)
                            for field in Profile._meta.fields
                            if field.get_internal_type() != 'AutoField' and
                            field.name not in ['user', 'guid']])
        self.private_settings = self.set_default_private_settings()
        self.t4_timezone_map = {'AST': 'Canada/Atlantic',
                             'EST': 'US/Eastern',
                             'CST': 'US/Central',
                             'MST': 'US/Mountain',
                             'AKST': 'US/Alaska',
                             'PST': 'US/Pacific',
                             'GMT': 'UTC'
                             }
        if self.uimport.group_id:
            [self.uimport.group] = Group.objects.filter(id=self.uimport.group_id)[:1] or [None]
        else:
            self.uimport.group = None

    def init_summary(self):
        return {
                 'insert': 0,
                 'update': 0,
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

    def process_user(self, idata, **kwargs):
        """
        Check if it's insert or update. If dry_run is False,
        do the import to the profile and user.

        :param user_data: a dictionary that includes the info of a user
        """
        self.user_data = idata.row_data
        user = None
        user_display = {
            'error': u'',
            'user': None,
            'action': ''
        }

        is_valid, error_msg = check_missing_fields(self.user_data,
                                                  self.key)

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
            if self.key == 'email':
                users = get_user_by_email(self.user_data['email'])
            elif self.key == 'first_name,last_name,email':
                users = get_user_by_fn_ln_email(
                                self.user_data['first_name'],
                                self.user_data['last_name'],
                                self.user_data['email'])
            elif self.key == 'first_name,last_name,phone':
                users = get_user_by_fn_ln_phone(
                                   self.user_data['first_name'],
                                   self.user_data['last_name'],
                                   self.user_data['phone'])
            elif self.key == 'first_name,last_name,company':
                users = get_user_by_fn_ln_company(
                                   self.user_data['first_name'],
                                   self.user_data['last_name'],
                                   self.user_data['company'])
            elif self.key == 'username':
                users = User.objects.filter(username__iexact=self.user_data['username'])

            if users:
                user_display['action'] = 'update'
                user_display['user'] = users[0]
                user = user_display['user']
            else:
                user_display['action'] = 'insert'

            if not self.dry_run:
                if user_display['action'] == 'insert':
                    self.summary_d['insert'] += 1
                else:
                    self.summary_d['update'] += 1

                self.field_names = list(self.user_data.keys())
                # now do the update or insert
                self.do_import_user(user, self.user_data, user_display)
                idata.action_taken = user_display['action']
                idata.save()
                return

        user_display.update({
            'first_name': self.user_data.get('first_name', u''),
            'last_name': self.user_data.get('last_name', u''),
            'email': self.user_data.get('email', u''),
            'username': self.user_data.get('username', u''),
            'phone': self.user_data.get('phone', u''),
            'company': self.user_data.get('company', u''),
        })

        return user_display

    def do_import_user(self, user, user_data, action_info):
        """
        Database import here - insert or update
        """
        user = user or User()
        username_before_assign = user.username

        # always remove user column
        if 'user' in self.field_names:
            self.field_names.remove('user')

        self.assign_import_values_from_dict(user, action_info['action'])

        user.username = user.username or spawn_username(
            fn=user_data.get('first_name', u''),
            ln=user_data.get('last_name', u''),
            em=user_data.get('email', u''))

        # clean username
        user.username = re.sub(r'[^\w+-.@]', u'', user.username)

        # make sure username is unique.
        if action_info['action'] == 'insert':
            user.username = make_username_unique(user.username)
        else:
            # it's update but a new username is assigned
            # check if its unique
            if user.username != username_before_assign:
                user.username = make_username_unique(user.username)

        # allow import with override of password
        if 'password' in self.field_names and self.uimport.override and user.password:
            user.set_password(user.password)

        # is_active; interactive or non-interactive
        if self.uimport.interactive:
            user.is_active = True
        else:
            user.is_active = False

        user.save()

        # process profile
        try:  # get or create
            profile = user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(
                user=user,
                creator=self.request_user,
                creator_username=self.request_user.username,
                owner=self.request_user,
                owner_username=self.request_user.username,
                **self.private_settings)

        self.assign_import_values_from_dict(profile, action_info['action'])
        profile.user = user

        if profile.status is None or profile.status == '' or \
            self.user_data.get('status', '') == '':
            profile.status = True
        if not profile.status_detail:
            profile.status_detail = 'active'
        else:
            profile.status_detail = profile.status_detail.lower()

        if profile.status_detail == 'active' and not profile.status:
            profile.status = True

        profile.save()

        # add to group
        if self.uimport.group:
            if not self.uimport.group.is_member(user):
                params = {'creator_id': self.request_user.pk,
                      'creator_username': self.request_user.username,
                      'owner_id': self.request_user.pk,
                      'owner_username': self.request_user.username}
                self.uimport.group.add_user(user, **params)

    def assign_import_values_from_dict(self, instance, action):
        """
        Assign the import value from a dictionary object
        - self.user_data.
        """
        if instance.__class__ == User:
            assign_to_fields = self.user_fields
        elif instance.__class__ == Profile:
            assign_to_fields = self.profile_fields

        for field_name in self.field_names:
            if field_name in assign_to_fields:
                if any([
                        action == 'insert',
                        self.uimport.override,
                        not hasattr(instance, field_name) or
                        getattr(instance, field_name) == '' or
                        getattr(instance, field_name) is None
                        ]):
                    value = self.user_data[field_name]
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
            if field.name == 'time_zone':
                if value not in pytz.all_timezones:
                    if value in self.t4_timezone_map:
                        value = self.t4_timezone_map[value]
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
                try:
                    value = dparser.parse(value)
                except:
                    value = None
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


def normalize_field_names(fieldnames):
    for i in range(0, len(fieldnames)):
        # clean up the fieldnames
        # ex: change First Name to first_name
        fieldnames[i] = fieldnames[i].lower().replace(' ', '_')

    return fieldnames


def user_import_parse_csv(mimport):
    """
    Parse csv data into a dictionary.
    """
    normalize_newline(mimport.upload_file.name)
    csv_reader = csv.reader(
        default_storage.open(mimport.upload_file.name, 'rU'), )
    fieldnames = next(csv_reader)
    fieldnames = normalize_field_names(fieldnames)

    data_list = []

    for row in csv_reader:
        if not row:
            continue
        data_list.append(dict(zip(fieldnames, row)))

    return fieldnames, data_list
