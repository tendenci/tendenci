import re
from datetime import datetime
from dateutil.parser import parse as dt_parse

from django.contrib.auth.models import User
from profiles.models import Profile

from profiles.models import Profile
from memberships.models import Membership, MembershipType
from memberships.utils import csv_to_dict, spawn_username, get_user

def clean_username(un):
    # clean username
    un = re.sub(r'[^a-zA-Z0-9._@]+', '', un)
    
    # soft truncate
    if len(un) > 30:
        un = un.split('@')[0]  # pray for email address

    # hard truncate
    return un[:30]

def is_duplicate(csv_dict, csv_dicts, key):
    """Check for duplicates of the element in the same csv file.
    If it is the first instance of the duplicates it will not be marked
    as a duplicate.
    """
    keys = key.split(',')
    dups = []
    for i in range(len(csv_dicts)):
        csv_dicts[i]['index_number'] = i
        cd = csv_dicts[i]
        match = True
        for k in keys:
            try:
                if cd[k] != csv_dict[k]:
                    match = False
                    break
            except KeyError:
                pass
        if match:
            dups.append(cd)
    if dups and dups.index(csv_dict) != 0:
        return True
    return False

def clean_field_name(field):

    if 'email' in field:
        field = 'email'

    field = field.lower()
    field = field.replace('-', '_')
    field = field.replace(' ', '_')
    return field

def parse_mems_from_csv(file_path, mapping, **kwargs):
    """
    Returns membership dictionary and stats dictionary

    stats:
        all, added, skipped

    memberships:
        username, fn, ln, email, 
        join dt, renew dt, expire dt, 
        added, skipped, renewal
    """
    from base.utils import is_blank

    membership_import = kwargs['membership_import']

    key = membership_import.key
    override = membership_import.override

    csv_dicts = csv_to_dict(file_path, machine_name=True)
    membership_dicts = []
    skipped = 0

    for csv_dict in csv_dicts:  # field mapping
        m = {}
        for app_field, csv_field in mapping.items():
            if csv_field:  # skip blank option
                # membership['username'] = 'charliesheen'
                m[clean_field_name(app_field)] = csv_dict.get(csv_field, '')

        user_keys = ['username', 'firstname', 'lastname', 'email']
        for user_key in user_keys:
            m[user_key] = m.get(user_key, '')



        null_date = datetime(1951, 1, 1)
        date_keys = ['joindate', 'renewdate', 'expiredate', 'joindt', 'renewdt', 'expiredt']
        for date_key in date_keys:
            m[date_key] = m.get(date_key)

        m['skipped'] = False  # skip if no type
        m['renewal'] = bool(m['renewdate'])

        user_kwargs = {}
        for i in key.split(','):
            user_kwargs[i] = m[i.replace('_','')]

        if 'username' in kwargs:
            kwargs['username'] = kwargs['username'][:30]

        user = None
        if not is_blank(user_kwargs):
            if key == 'member_number':
                membership = Membership.objects.first(**user_kwargs)
                user = membership.user
            else:
                user = get_user(**user_kwargs)

        if not user and m['username']:
            user = get_user(username=m['username'][:30])

        if user:
            if override:
                m['username'] = m['username'] or user.username
                m['firstname'] = m['firstname'] or user.first_name
                m['lastname'] = m['lastname'] or user.last_name
                m['email'] = m['email'] or user.email
            else:
                m['username'] = user.username or m['username']
                m['firstname'] = user.first_name or m['firstname']
                m['lastname'] = user.last_name or m['lastname']
                m['email'] = user.email or m['email']

        m['fullname'] = "%s %s" % (m.get('firstname', ''), m.get('lastname', ''))
        m['fullname'] = m['fullname'].strip()

        try:
            membership_type = MembershipType.objects.get(name = m['membershiptype'])
        except:
            membership_type = None
            m['skipped'] = True
            skipped = skipped + 1

        if not m['skipped']:
            if not user and not m['email']:
                # email required to create user
                m['skipped'] = True
                skipped = skipped + 1

        if membership_type and user:

            membership_exists = Membership.objects.filter(
                user=user, membership_type=membership_type).exists()

            if membership_exists:
                if not override:
                    m['skipped'] = True
                    skipped = skipped + 1
            elif is_duplicate(csv_dict, csv_dicts, key):
                m['skipped'] = True
                skipped = skipped + 1

        if m['joindate']:
            dt = dt_parse(m['joindate'])
            if dt > null_date:
                m['joindt'] = dt

        if m['renewdate']:
            dt = dt_parse(m['renewdate'])
            if dt > null_date:
                m['renewdt'] = dt

        if m['expiredate']:
            m['expiredt'] = dt_parse(m['expiredate'])

        if not m['expiredt']:
            if membership_type:
                m['expiredt'] = membership_type.get_expiration_dt(
                    join_dt=m['joindt'], 
                    renew_dt=m['renewdt'], 
                    renewal=m['renewal']
                )

        m['subscribedt'] = m['joindt'] or datetime.now()
        membership_dicts.append(m)

    total = len(membership_dicts)
    stats = {
        'all': total,
        'skipped': skipped,
        'added': total-skipped,
    }

    return membership_dicts, stats
    
