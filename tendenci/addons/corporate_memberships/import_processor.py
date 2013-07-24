import os
import csv
from decimal import Decimal
from datetime import datetime, date, timedelta
import dateutil.parser as dparser
import pytz

from django.core import exceptions
from django.contrib.auth.models import User

from tendenci.core.site_settings.utils import get_setting
from tendenci.addons.corporate_memberships.models import (
                                            CorpMembership,
                                            CorpProfile,
                                            CorpMembershipRep,
                                            CorporateMembershipType)
from tendenci.addons.corporate_memberships.utils import update_authorized_domains
from tendenci.addons.memberships.models import MembershipDefault
from tendenci.apps.profiles.models import Profile


class CorpMembershipImportProcessor(object):
    """
    Check and process (insert/update) a corporate membership.
    """
    def __init__(self, request_user, mimport,
                               dry_run=True, **kwargs):
        """
        :param mimport: a instance of MembershipImport
        :param dry_run: if True, do everything except updating the database.
        """
        self.key = mimport.key
        self.request_user = request_user
        self.mimport = mimport
        self.dry_run = dry_run
        self.summary_d = self.init_summary()
        self.corp_profile_fields = dict([(field.name, field) \
                            for field in CorpProfile._meta.fields \
                            if field.get_internal_type() != 'AutoField' and \
                            field.name not in ['guid']])
        self.corp_membership_fields = dict([(field.name, field) \
                            for field in CorpMembership._meta.fields \
                            if field.get_internal_type() != 'AutoField' and \
                            field.name not in ['user', 'guid',
                                               'corp_profile']])
        self.private_settings = self.set_default_private_settings()
        self.t4_timezone_map = {'AST': 'Canada/Atlantic',
                             'EST': 'US/Eastern',
                             'CST': 'US/Central',
                             'MST': 'US/Mountain',
                             'AKST': 'US/Alaska',
                             'PST': 'US/Pacific',
                             'GMT': 'UTC'
                             }
        self.t4_timezone_map_keys = self.t4_timezone_map.keys()

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

    def validate_fields(self, cmemb_data, key):
        """
        1. Check if we have enough data to process for this row.
        2. Check if this is an archived corporate membership.
        """
        error_msg = []

        if key == 'name':
            if not cmemb_data['company_name']:
                error_msg.append("Missing key 'company_name'.")
#         if 'status_detail' in cmemb_data.keys():
#             if cmemb_data['status_detail'] in ['archive', 'archived']:
#                 error_msg.append('No import for archived.')

        return ' '.join(error_msg)

    def process_corp_membership(self, cmemb_data, **kwargs):
        """
        Check if it's insert or update. If dry_run is False,
        do the import to the corpmembership.

        :param cmemb_data: a dictionary that includes the info
        of a corp_membership
        """
        self.cmemb_data = cmemb_data
        self.cmemb_data['name'] = self.cmemb_data['company_name']
        del self.cmemb_data['company_name']
        self.field_names = cmemb_data.keys()  # csv field names
        corp_memb_display = {}
        corp_memb_display['error'] = ''
        corp_memb_display['user'] = None
        status_detail = self.cmemb_data.get('status_detail', 'active')
        if status_detail == 'archived':
            status_detail = 'archive'
        if not status_detail in CorpMembership.VALID_STATUS_DETAIL:
            status_detail = 'active'
        self.cmemb_data['status_detail'] = status_detail
        expiration_dt = self.cmemb_data.get('expiration_dt', None)
        if expiration_dt:
            expiration_dt = dparser.parse(expiration_dt)

        error_msg = self.validate_fields(self.cmemb_data, self.key)

        # don't process if we have missing value of required fields
        if error_msg:
            corp_memb_display['error'] = error_msg
            corp_memb_display['action'] = 'skip'
            if not self.dry_run:
                self.summary_d['invalid'] += 1
        else:
            #if self.key == 'name':
            [corp_profile] = CorpProfile.objects.filter(
                    name=self.cmemb_data['name'])[:1] or [None]
            if corp_profile:
                corp_membs = CorpMembership.objects.filter(
                            corp_profile=corp_profile,
                            status_detail=status_detail)
                # there might be multiple archives, pick the one that
                # matches with the expiration_dt
                if status_detail == 'archive' and expiration_dt:
                    corp_membs = corp_membs.filter(
                            expiration_dt__year=expiration_dt.year,
                            expiration_dt__month=expiration_dt.month,
                            expiration_dt__day=expiration_dt.day
                            )
                [corp_memb] = corp_membs.order_by('-id')[:1] or [None]
            else:
                corp_memb = None

            if corp_profile:
                if corp_memb:
                    corp_memb_display['action'] = 'update'
                    corp_memb_display['corp_profile_action'] = 'update'
                    corp_memb_display['corp_memb_action'] = 'update'
                else:
                    corp_memb_display['action'] = 'mixed'
                    corp_memb_display['corp_profile_action'] = 'update'
                    corp_memb_display['corp_memb_action'] = 'insert'
            else:
                corp_memb_display['action'] = 'insert'
                corp_memb_display['corp_profile_action'] = 'insert'
                corp_memb_display['corp_memb_action'] = 'insert'

            if not self.dry_run:
                if corp_memb_display['action'] == 'insert':
                    self.summary_d['insert'] += 1
                elif corp_memb_display['action'] == 'update':
                    self.summary_d['update'] += 1
                else:
                    self.summary_d['update_insert'] += 1

                # now do the update or insert
                self.do_import_corp_membership(corp_profile, corp_memb,
                                                  corp_memb_display)
                # handle authorized_domain
                if 'authorized_domains' in self.field_names:
                    update_authorized_domains(corp_profile,
                                        self.cmemb_data['authorized_domains'])

                # handle dues_rep
                if 'dues_rep' in self.field_names:
                    self.update_dues_reps(corp_profile,
                                          self.cmemb_data['dues_rep'])

                return

        corp_memb_display.update({
                    'company_name': self.cmemb_data.get('name', ''),
                    'email': self.cmemb_data.get('email', ''),
                    'address': self.cmemb_data.get('address', ''),
                    'address2': self.cmemb_data.get('address2', ''),
                    'city': self.cmemb_data.get('city', ''),
                    'state': self.cmemb_data.get('state', ''),
                    'zip': self.cmemb_data.get('zip', ''),
                    'status_detail': self.cmemb_data.get('status_detail', ''),
                             })
        return corp_memb_display

    def update_dues_reps(self, corp_profile, dues_reps):
        """
        Update the dues reps for this corp_profile.
        """
        dues_reps = dues_reps.split(',')
        dues_reps_list = [name.strip() for name in dues_reps]
        dues_reps_users_list = []
        # get the user objects by username
        for username in dues_reps_list:
            [u] = User.objects.filter(username=username)[:1] or [None]
            if u:
                dues_reps_users_list.append(u)
        if dues_reps_users_list:
            # delete the existing dues reps
            CorpMembershipRep.objects.filter(corp_profile=corp_profile,
                                             is_dues_rep=True).delete()
            for u in dues_reps_users_list:
                dues_rep = CorpMembershipRep(
                                    corp_profile=corp_profile,
                                    user=u,
                                    is_dues_rep=True)
                dues_rep.save()

    def do_import_corp_membership(self, corp_profile, corp_memb, action_info):
        """
        Database import here - insert or update
        """
        # handle corp_profile
        if not corp_profile:
            corp_profile = CorpProfile()

        self.assign_import_values_from_dict(corp_profile, action_info['corp_profile_action'])

        if corp_profile.status == None or corp_profile.status == '' or \
            self.cmemb_data.get('status', '') == '':
            corp_profile.status = True
        if not corp_profile.status_detail:
            corp_profile.status_detail = 'active'
        else:
            corp_profile.status_detail = corp_profile.status_detail.lower()

        if not corp_profile.creator:
            corp_profile.creator = self.request_user
            corp_profile.creator_username = self.request_user.username
        if not corp_profile.owner:
            corp_profile.owner = self.request_user
            corp_profile.owner_username = self.request_user.username

        corp_profile.save()

        # corpmembership
        if not corp_memb:
            corp_memb = CorpMembership(
                    corp_profile=corp_profile,
                    creator=self.request_user,
                    creator_username=self.request_user.username,
                    owner=self.request_user,
                    owner_username=self.request_user.username,
                                     )

        self.assign_import_values_from_dict(corp_memb, action_info['corp_memb_action'])

        if corp_memb.status == None or corp_memb.status == '' or \
            self.cmemb_data.get('status', '') == '':
            corp_memb.status = True
        if not corp_memb.status_detail:
            corp_memb.status_detail = 'active'
        else:
            corp_memb.status_detail = corp_memb.status_detail.lower()

        # set to approved for active memberships
        if not corp_memb.approved:
            if corp_memb.status and corp_memb.status_detail == 'active':
                corp_memb.approved = True

        # corporate membership type
        if not hasattr(corp_memb, "corporate_membership_type") or \
                not corp_memb.corporate_membership_type:
            # last resort - pick the first available membership type
            corp_memb.corporate_membership_type = CorporateMembershipType.objects.all(
                                            ).order_by('id')[0]

        # no join_dt - set one
        if not hasattr(corp_memb, 'join_dt') or not corp_memb.join_dt:
            if corp_memb.status and corp_memb.status_detail == 'active':
                corp_memb.join_dt = datetime.now()

        # no expire_dt - get it via corporate_membership_type
        if not hasattr(corp_memb, 'expiration_dt') or not corp_memb.expiration_dt:
            if corp_memb.corporate_membership_type:
                expiration_dt = corp_memb.corporate_membership_type.get_expiration_dt(
                                            join_dt=corp_memb.join_dt)
                setattr(corp_memb, 'expiration_dt', expiration_dt)

        if not corp_memb.creator:
            corp_memb.creator = self.request_user
            corp_memb.creator_username = self.request_user.username
        if not corp_memb.owner:
            corp_memb.owner = self.request_user
            corp_memb.owner_username = self.request_user.username
        corp_memb.save()

        # bind members to their corporations by company names
        if self.mimport.bind_members:
            self.bind_members_to_corp_membership(corp_memb)

    def bind_members_to_corp_membership(self, corp_memb):
        corp_profile = corp_memb.corp_profile
        company_name = corp_profile.name
        user_ids = Profile.objects.filter(company=company_name
                                    ).values_list('user__id', flat=True)
        if user_ids:
            memberships = MembershipDefault.objects.filter(
                                    user__id__in=user_ids
                                    ).filter(status=True
                                    ).exclude(status_detail='archive')
            for membership in memberships:
                if not membership.corp_profile:
                    membership.corp_profile_id = corp_profile.id
                    membership.corporate_membership_id = corp_memb.id
                    membership.save()

    def is_active(self, corp_memb):
        return all([
                corp_memb.status,
                corp_memb.status_detail == 'active',
                not corp_memb.expiration_dt or corp_memb.expiration_dt > datetime.now()
                ])

    def assign_import_values_from_dict(self, instance, action):
        """
        Assign the import value from a dictionary object
        - self.cmemb_data.
        """
        if instance.__class__ == CorpProfile:
            assign_to_fields = self.corp_profile_fields
        else:
            assign_to_fields = self.corp_membership_fields
        # list of field names from the model
        # self.field_names is a list of field names from csv
        assign_to_fields_names = assign_to_fields.keys()

        for field_name in self.field_names:
            if field_name in assign_to_fields_names:
                if any([
                        action == 'insert',
                        self.mimport.override,
                        not hasattr(instance, field_name) or \
                        getattr(instance, field_name) == '' or \
                        getattr(instance, field_name) == None
                        ]):
                    value = self.cmemb_data[field_name]
                    value = self.clean_data(value,
                                            assign_to_fields[field_name])
                    setattr(instance, field_name, value)
                    #print field_name, value

        # if insert, set defaults for the fields not in csv.
        for field_name in assign_to_fields_names:
            if field_name not in self.field_names and action == 'insert':
                if field_name not in self.private_settings.keys():
                    if field_name not in ['creator', 'owner',
                                          'creator_username',
                                          'owner_username']:
                        value = self.get_default_value(
                                        assign_to_fields[field_name])
                        if value != None:
                            setattr(instance, field_name, value)

    def get_default_value(self, field):
        # if allows null or has default, return None
        if field.null or field.has_default():
            return None

        field_type = field.get_internal_type()

        if field_type == 'BooleanField':
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
            if not field.name in ['creator', 'owner']:
                [value] = field.related.parent_model.objects.all(
                                            )[:1] or [None]
                return value
            return None

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
                    if value in self.t4_timezone_map_keys:
                        value = self.t4_timezone_map[value]
            try:
                value = field.to_python(value)
            except exceptions.ValidationError:
                if field.has_default():
                    value = field.get_default()
                else:
                    value = ''

        elif field_type == 'BooleanField':
            if value == 'TRUE':
                value = True
            try:
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
            orignal_value = value
            # assume id for foreign key
            try:
                value = int(value)
            except:
                value = None

            if value:
                [value] = field.related.parent_model.objects.filter(
                                            pk=value)[:1] or [None]

            # membership_type - look up by name in case
            # they entered name instead of id
            if not value and field.name == 'corporate_membership_type':
                [value] = CorporateMembershipType.objects.filter(
                                            name=orignal_value)[:1] or [None]

            if not value and not field.null:
                if not field.name in ['creator', 'owner']:
                    # if the field doesn't allow null, grab the first one.
                    [value] = field.related.parent_model.objects.all(
                                            ).order_by('id')[:1] or [None]

        return value
