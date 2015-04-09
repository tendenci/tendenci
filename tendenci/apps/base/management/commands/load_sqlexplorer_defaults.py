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
('All Members',
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
('All Corporate Members',
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
('All Users in a Specific Group (replace <YOUR GROUP ID> with your group id)',
 """SELECT ug.name, u.first_name, u.last_name, u.email, u.username, u.is_staff,
     u.is_superuser, p.salutation, p.company, p.position_title, p.phone,
     p.address, p.address2, p.member_number, p.city, p.state, p.zipcode,
     p.country, p.url, p.sex, p.address_type, p.phone2, p.fax, p.work_phone,
     p.home_phone, p.mobile_phone
FROM auth_user u INNER JOIN profiles_profile p
ON u.id=p.user_id INNER JOIN user_groups_groupmembership ugm 
on u.id=ugm.member_id INNER JOIN user_groups_group ug on ug.id=ugm.group_id 
WHERE ug.id=<YOUR GROUP ID> 
AND ugm.status=True 
AND ugm.status_detail='active'"""),
                       )
            for title, sql in queries:
                query = Query(title=title,
                              sql=sql)
                query.save()
                print 'Inserted: ', title
                
        else:
            print 'NO default sqls loaded for SQL Explorer because django-sqlexplorer is not installed'