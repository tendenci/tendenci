import re
from datetime import datetime

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
        try:
            membership_type = MembershipType.objects.get(name = m['membership-type'])
        except:
            # no memtype
            membership_type = None
            m['skipped'] = True
        
        if membership_type and user:
            # already exists
            m['skipped'] = Membership.objects.filter(user=user, membership_type=membership_type).exists()
        
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
        
    return membership_dicts
    
def new_mems_from_csv(file_path, app, columns):
    """
    Create membership objects (not in database)
    Membership objects are based off of file (typically import)
    An extra field called columns can be passed in for field mapping
    A membership application is required
    """
    from profiles.models import Profile
    from django.db import IntegrityError
    NOW = datetime.now()

    membership_dicts = []
    for csv_dict in csv_to_dict(file_path):  # field mapping

        membership = {}
        for app_field, csv_field in columns.items():
            if csv_field:  # skip blank option
                # membership['username'] = 'charliesheen'
                membership[app_field] = csv_dict[csv_field]

        membership_dicts.append(membership)

    membership_set = []
    skipped_set = []

    def clean_username(un):
        import re

        # clean username
        un = re.sub(r'[^a-zA-Z0-9._]+', '', un)

        # soft truncate
        if len(un) > 30:
            un = un.split('@')[0]  # pray for email address

        # hard truncate
        return un[:30]

    for m in membership_dicts:
        # detect if renewal
        m['renewal'] = bool(m.get('renew-date'))

        # clean username
        username = clean_username(m['user-name'])

        try:  # note: cannot return multiple; usernames are unique
            user, created = User.objects.get_or_create(username = username)
        except (User.MultipleObjectsReturned, IntegrityError) as e:
            user = User.objects.filter(username = username)[0]
        

        try:  # if membership type exists; import membership
            membership_type = MembershipType.objects.get(name = m['membership-type'])
        except:
            for key in m.keys():
                m[slugify(key).replace('-', '_')] = m.pop(key)
            skipped_set.append(m)
            continue  # on to the next one
        
        try: join_dt = dt_parse(m['join-date'])
        except: join_dt = None
        try: renew_dt = dt_parse(m['renew-date'])
        except: renew_dt = None

        # tendenci 4 null date: 1951-01-01
        tendenci4_null_date = datetime(1951,1,1,0,0,0)
        if join_dt and join_dt <= tendenci4_null_date: join_dt = None
        if renew_dt and renew_dt <= tendenci4_null_date: renew_dt = None

        try: expire_dt = dt_parse(m['expire-date'])
        except: expire_dt = membership_type.get_expiration_dt(join_dt=join_dt, renew_dt=renew_dt, renewal=m.get('renewal'))

        # update user
        user.first_name = m.get('First Name') or user.first_name
        user.last_name = m.get('Last Name') or user.last_name
        user.email = m.get('E-Mail') or m.get('Email') or user.email
        user.save()


        try:
            # get profile
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist as e:
            # create profile
            profile = Profile.objects.create(
                user=user,
                creator=user,
                owner=user,
                owner_username = user.username,
            )
        except Profile.MultipleObjectsReturned as e:
            # or get first profile
            profile = Profile.objects.filter(
                user=user,
                creator=user,
                owner=user,
                owner_username = user.username,
            )[0]

        # update profile
        profile.company = m.get('Company') or profile.company
        profile.position_title = m.get('Position Title') or profile.position_title
        profile.address = m.get('Mailing Address') or profile.address
        profile.address2 = m.get('Address 2') or profile.address2
        profile.city = m.get('City') or profile.city
        profile.state = m.get('State') or profile.state
        profile.zipcode = m.get('Zip Code') or profile.zipcode
        profile.county = m.get('County') or profile.county
        profile.address_type = m.get('Address Type') or profile.address_type
        profile.work_phone = m.get('Work Phone') or profile.work_phone
        profile.home_phone = m.get('Home Phone') or profile.home_phone
        profile.mobile_phone = m.get('Mobile Phone') or profile.mobile_phone
        profile.email = user.email
        profile.email2 = m.get('E-mail 2') or profile.email2
        profile.url = m.get('Web Site') or profile.url

        if m.get('DOB'):
            profile.dob = dt_parse(m.get('DOB')) or datetime.now()

        profile.save()

        memberships = Membership.objects.filter(
            user=user,
            membership_type=membership_type,
        )

        # get subscribe_dt
        subscribe_dt = join_dt or datetime.now()
        
        if 'cc' in m.get('payment-method', ''):
            payment_method_id = 1
        elif 'check' in m.get('payment-method', ''):
            payment_method_id = 2
        elif 'cash' in m.get('payment-method', ''):
            payment_method_id = 3
        else:
            payment_method_id = None

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

            membership.payment_method_id = payment_method_id

            membership.renewal = m.get('renewal')
            membership.status = m.get('status') or True
            membership.status_detail = m.get('status-detail') or 'Active'
            membership.expire_dt = expire_dt

        try:  # bind corporate membership with membership
            corp_memb = CorporateMembership.objects.get(name=m.get('corp-membership-name'))
            membership.membership_type = corp_memb.corporate_membership_type.membership_type
            membership.corporate_membership_id = corp_memb.pk
        except:
            pass

        membership.m = m  # temp append dict

        membership_set.append(membership)

    return membership_set, skipped_set
