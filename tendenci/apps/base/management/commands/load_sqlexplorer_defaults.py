import os
from optparse import make_option
from random import randint
from boto.s3.connection import S3Connection

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Insert default sqls for explorer"

    def handle(self, **options):
        if 'explorer' in settings.INSTALLED_APPS:
            from explorer.models import Query
            queries = (
('All Interactive Users',
'All Interactive Users - People Who Can Login to the Site',
"""SELECT u.first_name, u.last_name, u.email, u.username, u.is_staff, u.is_superuser,  
        p.salutation, p.company, p.position_title, p.phone, p.address, p.address2, 
        p.member_number, p.city, p.state, p.zipcode, p.country, p.url, p.sex,
        p.address_type, p.phone2, p.fax, p.work_phone, p.home_phone, p.mobile_phone,
        p.notes, p.admin_notes
FROM auth_user u INNER JOIN profiles_profile p
ON u.id=p.user_id
WHERE u.is_active=True
AND p.status=True
AND p.status_detail='active'"""),
('All Memberships',
'All Memberships',
"""SELECT u.first_name, u.last_name, u.email, u.username, u.is_staff, u.is_superuser,
        p.salutation, p.company, p.position_title, p.phone, p.address, p.address2,
        p.member_number, p.city, p.state, p.zipcode, p.country, p.url, p.sex,
        p.address_type, p.phone2, p.fax, p.work_phone, p.home_phone, p.mobile_phone,
        m.membership_type_id, m.renewal, m.certifications, m.work_experience,
        m.referer_url, m.referral_source, m.join_dt, m.expire_dt, m.renew_dt,
        m.primary_practice, m.how_long_in_practice, m.application_approved,
        m.application_approved_dt, m.areas_of_expertise, m.home_state,
        m.year_left_native_country, m.network_sectors, m.networking,
        m.government_worker, m.government_agency, m.license_number,
        m.license_state, m.status_detail
FROM auth_user u
INNER JOIN profiles_profile p
ON u.id=p.user_id
INNER JOIN memberships_membershipdefault m
ON m.user_id=u.id
WHERE u.is_active=True
AND p.status=True
AND m.status_detail <> 'archive'"""),
('All Corporate Memberships',
'All corporate memberships',
 """SELECT cp.name, cp.address, cp.address2, cp.city, cp.state, cp.zip, cp.country,
     cp.phone, cp.email, cp.url, cp.number_employees, cp.chapter, cp.tax_exempt,
     cp.annual_revenue, cp.annual_ad_expenditure, cp.description, cp.expectations,
     cp.notes, cp.referral_source, cp.ud1, cp.ud2, cp.ud3, cp.ud4, cp.ud5, cp.ud6,
     cp.ud7, cp.ud8, cm.corporate_membership_type_id, cm.renewal, cm.renew_dt,
     cm.join_dt, cm.expiration_dt, cm.approved, cm.admin_notes, cm.status_detail 
FROM corporate_memberships_corpprofile cp
INNER JOIN corporate_memberships_corpmembership cm
ON cp.id=cm.corp_profile_id
WHERE cm.status_detail <> 'archive'"""),
('Users By Group ID (All Groups)',
'All groups - dump this into Excel and filter by the group_name field as needed',
"""SELECT ug.name as group_name, u.first_name, u.last_name, u.email, u.username, u.is_staff, 
      u.is_superuser, p.salutation, p.company, p.position_title, p.phone, 
      p.address, p.address2, p.member_number, p.city, p.state, p.zipcode, 
      p.country, p.url, p.sex, p.address_type, p.phone2, p.fax, p.work_phone, 
      p.home_phone, p.mobile_phone 
FROM auth_user u 
INNER JOIN profiles_profile p ON u.id=p.user_id 
INNER JOIN user_groups_groupmembership ugm on u.id=ugm.member_id 
INNER JOIN user_groups_group ug on ug.id=ugm.group_id 
WHERE ug.id>0
AND ugm.status=True 
AND ugm.status_detail='active'"""),
('Users By Group ID (Edit the Group ID)',
'Users by Group ID - this query shows group id = 1 on line number 10, so edit that for whichever group you are looking for.',
"""SELECT ug.name as group_name, u.first_name, u.last_name, u.email, u.username, u.is_staff, 
      u.is_superuser, p.salutation, p.company, p.position_title, p.phone, 
      p.address, p.address2, p.member_number, p.city, p.state, p.zipcode, 
      p.country, p.url, p.sex, p.address_type, p.phone2, p.fax, p.work_phone, 
      p.home_phone, p.mobile_phone 
FROM auth_user u 
INNER JOIN profiles_profile p ON u.id=p.user_id 
INNER JOIN user_groups_groupmembership ugm on u.id=ugm.member_id 
INNER JOIN user_groups_group ug on ug.id=ugm.group_id 
WHERE ug.id=1 
AND ugm.status=True 
AND ugm.status_detail='active'"""),
('Tables - List All Database Tables',
'A list of all tables including system tables',
"""select tablename from pg_tables"""),
('Users In the Database On The Site, Not All Can Login',
'This lists everyone in the auth_user table which is the default django table for authentication but also used for anyone who has filled out a contact form. The passwords are encrypted and cant be decrypted (no way around that) but it does have the basics of all humans (does NOT mean they can login.)',
"""select id, first_name, last_name, email, username, last_login, is_superuser, is_staff, is_active, date_joined  from auth_user;"""),
('Users in Database with Membership Details',
'Users in Database with Membership Details',
"""select u.id, u.first_name, u.last_name, u.email, u.username, u.last_login, u.is_superuser, u.is_staff, u.is_active, m.member_number, m.join_dt, m.expire_dt
from auth_user u
inner join memberships_membershipdefault m on m.user_id = u.id
where m.status=true
and m.status_detail<>'archive'"""),
)
            for title, description, sql in queries:
                query = Query(title=title,
                              description=description,
                              sql=sql)
                query.save()
                print 'Inserted: ', title
                
        else:
            print 'NO default sqls loaded for SQL Explorer because django-sqlexplorer is not installed'