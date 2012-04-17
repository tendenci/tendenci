import os
from datetime import datetime
from dateutil.parser import parse as dt_parse

from django.contrib.auth.models import User
from django.conf import settings

from celery.task import Task
from celery.registry import tasks

from profiles.models import Profile

from corporate_memberships.models import CorporateMembership
from memberships.models import (AppEntry, AppField, AppFieldEntry, 
    MembershipType, Membership, MembershipImport)
from memberships.importer.utils import (parse_mems_from_csv,
    clean_username)

class ImportMembershipsTask(Task):

    def run(self, memport_id, fields, **kwargs):
        from django.template.defaultfilters import slugify
        from memberships.utils import get_user

        #get parsed membership dicts
        imported = []
        mems, stats = parse_mems_from_csv(file_path, fields)

        for m in mems:
            if not m['skipped']:
                # get membership type.
                # this should not throw DNE errors
                # otherwise it should have been marked skipped.
                membership_type = MembershipType.objects.get(name=m['membershiptype'])
                
                # initialize dates
                join_dt = m['joindt']
                renew_dt = m['renewdt']
                expire_dt = m['expiredt']
                subscribe_dt = m['subscribedt']

                credit_cards = ('cc','credit','creditcard')
                checks = ('check',)
                cash = ('cash',)

                # determine payment method id
                # this assumes that the default payment methods are used.
                payment_method = slugify(m.get('paymentmethod', '')).replace('-','')
                payment_method_id = None
                if payment_method in credit_cards:
                    payment_method_id = 1
                elif payment_method in checks:
                    payment_method_id = 2
                elif payment_method in cash:
                    payment_method_id = 3

                # get or create user
                user = get_user(username = m['username']) or \
                    User.objects.create_user(m['username'], m['email'])

                user.first_name = user.first_name or m['firstname']
                user.last_name = user.last_name or m['lastname']
                user.email = user.email or m['email']
                user.save()

                # get or create profile
                try:
                    profile = Profile.objects.get(user=user)
                except Profile.MultipleObjectsReturned:
                    profile = Profile.objects.filter(user =user)[0]
                except Profile.DoesNotExist:
                    profile = Profile.objects.create_profile(user)

                # update profile
                if memport.override == 0:
                    if not profile.company:
                        profile.company = m.get('company') or profile.company
                    if not profile.position_title:
                        profile.position_title = m.get('positiontitle') or profile.position_title
                    if not profile.address:
                        profile.address = m.get('mailingaddress') or profile.address
                    if not profile.address2:
                        profile.address2 = m.get('address2') or profile.address2
                    if not profile.city:
                        profile.city = m.get('city') or profile.city
                    if not profile.state:
                        profile.state = m.get('state') or profile.state
                    if not profile.zipcode:
                        profile.zipcode = m.get('zipcode') or profile.zipcode
                    if not profile.country:
                        profile.country = m.get('county') or profile.county
                    if not profile.address_type:
                        profile.address_type = m.get('addresstype') or profile.address_type
                    if not profile.work_phone:
                        profile.work_phone = m.get('workphone') or profile.work_phone
                    if not profile.home_phone:
                        profile.home_phone = m.get('homephone') or profile.home_phone
                    if not profile.mobile_phone:
                        profile.mobile_phone = m.get('mobilephone') or profile.mobile_phone
                    if profile.email:
                        profile.email = user.email
                    if not profile.email2:
                        profile.email2 = m.get('email2') or profile.email2
                    if not profile.url:
                        profile.url = m.get('website') or profile.url
                    if not profile.dob:
                        if m.get('dob'):
                            profile.dob = dt_parse(m.get('dob')) or datetime.now()
                else:
                    profile.company = m.get('company') or profile.company
                    profile.position_title = m.get('positiontitle') or profile.position_title
                    profile.address = m.get('mailingaddress') or profile.address
                    profile.address2 = m.get('address2') or profile.address2
                    profile.city = m.get('city') or profile.city
                    profile.state = m.get('state') or profile.state
                    profile.zipcode = m.get('zipcode') or profile.zipcode
                    profile.county = m.get('county') or profile.county
                    profile.address_type = m.get('addresstype') or profile.address_type
                    profile.work_phone = m.get('workphone') or profile.work_phone
                    profile.home_phone = m.get('homephone') or profile.home_phone
                    profile.mobile_phone = m.get('mobilephone') or profile.mobile_phone
                    profile.email = user.email
                    profile.email2 = m.get('email2') or profile.email2
                    profile.url = m.get('website') or profile.url
                    if m.get('dob'):
                        profile.dob = dt_parse(m.get('dob')) or datetime.now()
                
                profile.save()
                
                print user.pk

                # get or create membership
                # relation does not hold unique constraints
                # so we assume the first hit is the correct membership
                # if it exists.
                memberships = Membership.objects.filter(
                    user=user,
                    membership_type=membership_type,
                )
                if memberships:
                    membership = memberships[0]
                else:
                    membership = Membership()
                    membership.ma = app
                    membership.user = user
                    membership.membership_type = membership_type
                    membership.member_number = m.get('membernumber') or 0
                    membership.owner = user
                    membership.creator = user
                    membership.subscribe_dt = subscribe_dt
                    membership.payment_method_id = payment_method_id
                    membership.renewal = m.get('renewal')
                    membership.status = m.get('status') or True
                    membership.status_detail = m.get('statusdetail') or 'Active'
                    membership.expire_dt = expire_dt
                # save membership
                membership.save()
                
                # bind corporate membership with membership if it exists
                corp_memb_name = m.get('corpmembershipname')
                if corp_memb_name:
                    try:
                        corp_memb = CorporateMembership.objects.get(name=corp_memb_name)
                        membership.membership_type = corp_memb.corporate_membership_type.membership_type
                        membership.corporate_membership_id = corp_memb.pk
                        membership.save()
                    except CorporateMembership.DoesNotExist:
                        pass
                
                # create entry
                entry = AppEntry.objects.create(
                    app = app,
                    user = membership.user,
                    entry_time = datetime.now(),
                    membership = membership,  # pk required here
                    is_renewal = membership.renewal,
                    is_approved = True,
                    decision_dt = membership.subscribe_dt,
                    judge = membership.creator,
                    creator=membership.creator,
                    creator_username=membership.creator_username,
                    owner=membership.owner,
                    owner_username=membership.owner_username,
                    allow_anonymous_view=False,
                )

                # create entry fields
                for key, value in fields.items():

                    app_fields = AppField.objects.filter(app=app, field_name=key)
                    if app_fields and m.get(key):

                        try:
                            value = unicode(m.get(unicode(key)))
                        except (UnicodeDecodeError) as e:
                            value = ''

                        AppFieldEntry.objects.create(
                            entry=entry,
                            field=app_fields[0],
                            value=value,
                        )

                # update membership number
                if not membership.member_number:
                    membership.member_number = AppEntry.objects.count() + 1000
                    membership.save()

                # add user to group
                membership.membership_type.group.add_user(membership.user)

                # append to imported list
                imported.append(membership)
                
        return imported, stats
