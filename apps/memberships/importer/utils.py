import re
from datetime import datetime
from dateutil.parser import parse as dt_parse

from django.contrib.auth.models import User

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
    
def clean_field_name(field):

    if 'email' in field:
        field = 'email'

    field = field.lower()
    field = field.replace('-', '_')
    field = field.replace(' ', '_')
    return field

def parse_mems_from_csv(file_path, mapping, parse_range=None):
    """
    Parse membership entries from a csv file.
    An extra field called columns can be passed in for field mapping
    parse_range is the range of rows to be parsed from the csv.
    Entries without a Membership Type will be marked as skipped.
    Entries that are already in the database will be marked as skipped.
    """

    membership_dicts = []
    skipped = 0
    for csv_dict in csv_to_dict(file_path, machine_name=True):  # field mapping

        m = {}
        for app_field, csv_field in mapping.items():
            if csv_field:  # skip blank option
                # membership['username'] = 'charliesheen'
                m[clean_field_name(app_field)] = csv_dict.get(csv_field, '')

        # get user via username or email
        if m.get('username'):
            # truncate the username at 30 since it if doesn't exist and is longer than 30
            # it will get truncated on insert. This way a subsequent import will match the username
            # correctly if the same 30+ length username is used
            user = get_user(username=m.get('username')[:30])
        elif m.get('email'):
            user = get_user(email=m.get('email'))

        # if user; take user info
        # if not; take form info
        # ------------------------

        if user:
            m['username'] = user.username
            m['fullname'] = user.get_full_name()
            m['firstname'] = user.first_name
            m['lastname'] = user.last_name
            m['email'] = user.email
        else:
            m['username'] = m.get('username') or spawn_username(m['email'])

            m['fullname'] = "%s %s" % (m.get('first_name', ''), m.get('last_name', ''))
            m['fullname'] = m.get('fullname', '').strip()

            m['firstname'] = m.get('firstname', '')
            m['lastname'] = m.get('lastname', '')
            m['email'] = m.get('email', '')

        # skip importing a record if
        # membership type does not exist
        # membership record already exists

        #check if should be skipped or not
        m['skipped'] = False
        try:
            membership_type = MembershipType.objects.get(name = m['membershiptype'])
        except:
            # no memtype
            membership_type = None
            m['skipped'] = True
            skipped = skipped + 1
        
        if membership_type and user:
            # already exists
            mem_type_exists = Membership.objects.filter(user=user, membership_type=membership_type).exists()
            if mem_type_exists:
                m['skipped'] = True
                skipped = skipped + 1
        
        # detect if renewal
        m['renewal'] = bool(m.get('renewdate'))

        #update the dates
        try:
            join_dt = dt_parse(m['joindate'])
        except:
            join_dt = None
        try:
            renew_dt = dt_parse(m['renewdate'])
        except:
            renew_dt = None
        
        # tendenci 4 null date: 1951-01-01
        tendenci4_null_date = datetime(1951,1,1,0,0,0)
        if join_dt and join_dt <= tendenci4_null_date:
            join_dt = None
        if renew_dt and renew_dt <= tendenci4_null_date:
            renew_dt = None
        
        subscribe_dt = join_dt or datetime.now()
        
        try:
            expire_dt = dt_parse(m['expiredate'])
        except:
            if membership_type:
                expire_dt = membership_type.get_expiration_dt(join_dt=join_dt, renew_dt=renew_dt, renewal=m.get('renewal'))
            else:
                expire_dt = None
        
        m['joindt'] = join_dt
        m['renewdt'] = renew_dt
        m['expiredt'] = expire_dt
        m['subscribedt'] = subscribe_dt
        
        membership_dicts.append(m)
    
    total = len(membership_dicts)
    stats = {
        'all': total,
        'skipped': skipped,
        'added': total-skipped,
        }
    return membership_dicts, stats
    
