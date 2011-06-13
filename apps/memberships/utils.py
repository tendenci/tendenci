import os
import csv
from dateutil.parser import parse as dt_parse
from datetime import datetime
from django.conf import settings
from django.utils import simplejson
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from memberships.models import AppField, Membership, MembershipType


def get_default_membership_fields(use_for_corp=False):
    json_file_path = os.path.join(settings.PROJECT_ROOT,
        'apps/memberships/fixtures/default_membership_application_fields.json')
    json_file = open(json_file_path, 'r')
    data = ''.join(json_file.read())
    json_file.close()
    
    field_list = simplejson.loads(data)
    
    # add default fields for corp. individuals
    if use_for_corp:
        corp_field_list = get_default_membership_corp_fields()
    else:
        corp_field_list = None
        
    if field_list:
        if corp_field_list:
            field_list = field_list + corp_field_list
    else:
        field_list = corp_field_list

    
    return field_list

def get_default_membership_corp_fields():
    json_file_path = os.path.join(settings.PROJECT_ROOT,
        'apps/memberships/fixtures/default_membership_application_fields_for_corp.json')
    json_file = open(json_file_path, 'r')
    data = ''.join(json_file.read())
    json_file.close()
    
    corp_field_list = simplejson.loads(data)
    
    return corp_field_list

def edit_app_update_corp_fields(app):
    """
    Update the membership application's corporate membership fields (corporate_membership_id)
    when editing a membership application.
    """
    if app:
        try:  
            app_field = AppField.objects.get(app=app, field_type='corporate_membership_id')
            if not app.use_for_corp:
                if not hasattr(app, 'corp_app'):
                    app_field.delete()
                else:
                    app.use_for_corp = 1
                    app.save()
        except AppField.DoesNotExist:
            if app.use_for_corp:
                field_list = get_default_membership_corp_fields()
                for field in field_list:
                    field.update({'app':app})
                    AppField.objects.create(**field)

def get_corporate_membership_choices():
    cm_list = [(0, 'SELECT ONE')]
    from django.db import connection
    # use the raw sql because we cannot import CorporateMembership in the memberships app
    cursor = connection.cursor()
    cursor.execute("""
                SELECT id, name 
                FROM corporate_memberships_corporatemembership 
                WHERE status=1 AND status_detail='active' 
                ORDER BY name """ ) 
    account_numbers = []
    for row in cursor.fetchall():
        cm_list.append((row[0], row[1]))
    
    return cm_list

def csv_to_dict(file_path):
    """
    Returns a list of dicts. Each dict represents record.
    """
    csv_file = csv.reader(open(file_path))
    col = csv_file.next()
    lst = []

    for row in csv_file:
        entry = {}
        for i in xrange(len(col)):
            entry[col[i]] = row[i]
        lst.append(entry)

    return lst  # list of dictionaries

def new_mems_from_csv(file_path, app, columns):
    """
    Create membership objects (not in database)
    Membership objects are based off of file (typically import)
    An extra field called columns can be passed in for field mapping
    A membership application is required
    """

    membership_dicts = []
    for membership in csv_to_dict(file_path):  # field mapping
        for native_column, foreign_column in columns.items():

            if foreign_column:  # skip blank option
                # membership['username'] = 'charliesheen'
                membership[native_column] = membership[foreign_column]

        membership_dicts.append(membership)

    membership_set = []

    for m in membership_dicts:

        # detect if renewal
        m['renewal'] = bool(m['renew-date'])

        try: # if user exists; import membership
            user = User.objects.get(username = m['user-name'])
        except:
            continue  # on to the next one

        try:  # if membership type exists; import membership
            membership_type = MembershipType.objects.get(name = m['membership-type'])
        except:
            continue  # on to the next one

        try: join_dt = dt_parse(m['join-date'])
        except: join_dt = None
        try: renew_dt = dt_parse(m['renew-date'])
        except: renew_dt = None

        try: expire_dt = dt_parse(m['expire-date'])
        except: expire_dt = membership_type.get_expiration_dt(join_dt=join_dt, renew_dt=renew_dt, renewal=m.get('renewal'))

        user_attrs = (
            m.get('First Name'),
            m.get('Last Name'),
            m.get('Email'),
        )

        # update user; TODO use field types for more optimal import
        if any(user_attrs):
            user.first_name = m.get('First Name') or user.first_name
            user.last_name = m.get('Last Name') or user.last_name
            user.email = m.get('Email') or user.email
            user.save()

        memberships = Membership.objects.filter(
            user=user,
            membership_type=membership_type,
        )

        # get subscribe_dt
        if renew_dt: subscribe_dt = renew_dt
        elif join_dt: subscribe_dt = join_dt
        else: subscribe_dt = datetime.now()

        if memberships:  # get membership record
            membership = memberships[0]
        else:  # create membership record
            membership = Membership()
            membership.ma = app
            membership.user = user
            membership.membership_type = membership_type
            membership.member_number = m.get('member-number') or 0
            membership.owner = user
            membership.creator = user
            membership.subscribe_dt = subscribe_dt
            membership.payment_method = m.get('payment-method') or ''
            membership.renewal = m.get('renewal')
            membership.status = m.get('status') or True
            membership.status_detail = m.get('status-detail') or 'Active'
            membership.expire_dt = expire_dt

        membership.m = m

        membership_set.append(membership)

    return membership_set

def is_import_valid(file_path):
    """
    Run import file against required files
    'username' and 'membership-type' are required fields
    """
    memberships = csv_to_dict(file_path)  # list of membership dicts
    membership_keys = [slugify(m) for m in memberships[0].keys()]
    required = ('username','membership_type')
    requirements = [r in membership_keys for r in required]

    return all(requirements)

