import os
import csv
from datetime import datetime
from django.conf import settings
from django.utils import simplejson
from django.contrib.auth.models import User
from memberships.models import AppField, Membership, MembershipType
from user_groups.models import GroupMembership

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
    
def import_csv(file):
    """
    Returns a list of dicts. Each dict represents
    a foreign membership record.
    """
    membership_csv = csv.reader(open(str(file), 'U'))
    headers = membership_csv.next()
    mems = list()
    for row in membership_csv:
        entry = dict()
        for i in range(len(headers)):
            entry[headers[i]] = row[i]
        mems.append(entry)
    return mems

def new_mems_from_csv(file, app, creator_id):
    """
    Creates new memberships based on a Tendenci 4 CSV file
    """
    from django.db import IntegrityError
    from haystack.query import SearchQuerySet
    from memberships.models import AppEntry, AppField, AppFieldEntry

    archive = False
    memberships_dicts = import_csv(file)
    creator = User.objects.get(id=creator_id)

    membership_set = []
    for csv in memberships_dicts:

        try: membership_type = MembershipType.objects.get(name = csv['membershiptype'])
        except: continue  # on to the next one

        user = User.objects.get(id=csv['userid'])

        create_dt = datetime.strptime(csv['createdatetime'], '%b %d %Y')
        memberships = Membership.objects.filter(
            member_number=csv['Member ID (member record)'],
            subscribe_dt=create_dt.strftime('%Y-%m-%d'),
        )

        # get or create membership
        if memberships:
            membership = memberships[0]
        else:
            membership = Membership(**{
                'user':user,
                'member_number': csv['Member ID (member record)'],
                'creator_id': creator_id,
                'owner_id': creator_id,
                'membership_type': membership_type,
                'join_dt': datetime.strptime(csv['Join Date Time'], '%b %d %Y'),
                'renew_dt': datetime.strptime(csv['Renew Date Time'], '%b %d %Y'),
                'subscribe_dt': datetime.strptime(csv['createdatetime'], '%b %d %Y'),
                'corporate_membership_id': csv['Corporate Membership ID'],
                'payment_method': csv["Payment Method"],
                'ma': app,
                'renewal': csv['renewal'],
                'status': csv['Status'],
                'status_detail': csv['Status Detail'],
                'guid':csv['guid'],
                'expiration_dt': datetime.strptime(csv["Expiration Date Time"], '%b %d %Y'),
            })

        membership_set.append(membership)


    return membership_set

        # entry, is_created = AppEntry.objects.get_or_create(
        #     app=app,
        #     user=membership.user,
        #     membership=membership,
        #     entry_time=create_dt,
        #     is_renewal=membership.renewal,
        #     is_approved=True,
        #     decision_dt=create_dt,
        #     judge=membership.creator,
        #     creator=membership.creator,
        #     creator_username=membership.creator_username,
        #     owner=membership.owner,
        #     owner_username=membership.owner_username,
        # )

        # print membership,
        # if membership_sqs: print '(existed)', 
        # else: print '(created)',
        # print membership.subscribe_dt



        # try:
        #     mem_type = MembershipType.objects.get(name=m['membershiptype'])
        #     user = User.objects.get(id=m['userid'])

        #     # group_membership = GroupMembership()
        #     # group_membership.group = mem_type.group
        #     # group_membership.member = user
        #     # group_membership.creator_id = creator.id
        #     # group_membership.creator_username = creator.username
        #     # group_membership.owner_id =  user.id
        #     # group_membership.owner_username = user.username
        #     # group_membership.save()

        #     print "membership", membership

        # except:
        #     import sys
        #     print "error", sys.exc_info()[1]
            
