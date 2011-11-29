import re
from datetime import datetime
from dateutil.parser import parse as dt_parse

from django.contrib.auth.models import User

from memberships.models import Membership, MembershipType
from memberships.utils import csv_to_dict

def clean_username(un):
    # clean username
    un = re.sub(r'[^a-zA-Z0-9._]+', '', un)
    
    # soft truncate
    if len(un) > 30:
        un = un.split('@')[0]  # pray for email address
    
    # hard truncate
    return un[:30]
    
def clean_field_name(name):
    name = name.lower()
    name = name.replace('-', '_')
    name = name.replace(' ', '_')
    return name

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
    for csv_dict in csv_to_dict(file_path):  # field mapping
    
        m = {}
        for app_field, csv_field in mapping.items():
            if csv_field:  # skip blank option
                # membership['username'] = 'charliesheen'
                m[clean_field_name(app_field)] = csv_dict[csv_field]
        
        # clean username
        username = clean_username(m['user_name'])
        m['user_name'] = username
        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            user = None
        
        # update full name and email
        if user:
            first_name = user.first_name
            last_name = user.last_name
            email = user.email
        else:
            first_name = m.get('first_name')
            last_name = m.get('last_name')
            email = m.get('e_mail') or m.get('email')
        
        if user:
            m['full_name'] = user.get_full_name()
        else:
            if first_name or last_name:
                m['full_name'] = "%s %s" % (first_name, last_name)
        m['email'] = email
                
        #check if should be skipped or not
        m['skipped'] = False
        try:
            membership_type = MembershipType.objects.get(name = m['membership_type'])
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
        m['renewal'] = bool(m.get('renew_date'))

        #update the dates
        try:
            join_dt = dt_parse(m['join_date'])
        except:
            join_dt = None
        try:
            renew_dt = dt_parse(m['renew_date'])
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
            expire_dt = dt_parse(m['expire_date'])
        except:
            if membership_type:
                expire_dt = membership_type.get_expiration_dt(join_dt=join_dt, renew_dt=renew_dt, renewal=m.get('renewal'))
            else:
                expire_dt = None
        
        m['join_dt'] = join_dt
        m['renew_dt'] = renew_dt
        m['expire_dt'] = expire_dt
        m['subscribe_dt'] = subscribe_dt
        
        membership_dicts.append(m)
    
    total = len(membership_dicts)
    stats = {
        'all': total,
        'skipped': skipped,
        'added': total-skipped,
        }
    return membership_dicts, stats
    
