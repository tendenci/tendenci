from datetime import datetime
from dateutil.parser import parse as dt_parse

from django.contrib.auth.models import User

from celery.task import Task
from celery.registry import tasks

from profiles.models import Profile

from corporate_memberships.models import CorporateMembership
from memberships.models import AppEntry, AppField, AppFieldEntry, MembershipType, Membership
from memberships.importer.utils import parse_mems_from_csv

class ImportMembershipsTask(Task):

    def run(self, app, file_path, fields, **kwargs):
        #get parsed membership dicts
        imported = []
        mems, stats = parse_mems_from_csv(file_path, fields)
        for m in mems:
            if not m['skipped']:
                # get membership type.
                # this should not throw DNE errors
                # otherwise it should have been marked skipped.
                membership_type = MembershipType.objects.get(name=m['membership_type'])
                
                # initialize dates
                join_dt = m['join_dt']
                renew_dt = m['renew_dt']
                expire_dt = m['expire_dt']
                subscribe_dt = m['subscribe_dt']
                
                # determine payment method id
                # this assumes that the default payment methods are used.
                payment_method = m.get('payment_method', '')
                if 'cc' in payment_method:
                    payment_method_id = 1
                elif 'check' in payment_method:
                    payment_method_id = 2
                elif 'cash' in payment_method:
                    payment_method_id = 3
                else:
                    payment_method_id = None
                
                # get or create User
                username = m['user_name']
                try:
                    user = User.objects.get(username = username)
                except User.DoesNotExist:
                    # Maybe we should set a password here too?
                    user = User(username = username)
                # update user
                user.first_name = m.get('first_name')
                user.last_name = m.get('last_name')
                user.email = m.get('email')
                #save user
                user.save()
                
                # get or create profile
                try:
                    profile = Profile.objects.get(user=user)
                except Profile.DoesNotExist:
                    profile = Profile.objects.create(
                        user=user,
                        creator=user,
                        owner=user,
                        owner_username = user.username,
                    )
                # update profile
                profile.company = m.get('company') or profile.company
                profile.position_title = m.get('position_title') or profile.position_title
                profile.address = m.get('mailing_address') or profile.address
                profile.address2 = m.get('address_2') or profile.address2
                profile.city = m.get('city') or profile.city
                profile.state = m.get('state') or profile.state
                profile.zipcode = m.get('zip_code') or profile.zipcode
                profile.county = m.get('county') or profile.county
                profile.address_type = m.get('address_type') or profile.address_type
                profile.work_phone = m.get('work_phone') or profile.work_phone
                profile.home_phone = m.get('home_phone') or profile.home_phone
                profile.mobile_phone = m.get('mobile_phone') or profile.mobile_phone
                profile.email = user.email
                profile.email2 = m.get('e_mail_2') or m.get('email_2') or profile.email2
                profile.url = m.get('web_site') or profile.url
                if m.get('dob'):
                    profile.dob = dt_parse(m.get('dob')) or datetime.now()
                
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
                    membership.member_number = m.get('member_number') or 0
                    membership.owner = user
                    membership.creator = user
                    membership.subscribe_dt = subscribe_dt
                    membership.payment_method_id = payment_method_id
                    membership.renewal = m.get('renewal')
                    membership.status = m.get('status') or True
                    membership.status_detail = m.get('status_detail') or 'Active'
                    membership.expire_dt = expire_dt
                # save membership
                membership.save()
                
                # bind corporate membership with membership if it exists
                corp_memb_name = m.get('corp_membership_name', None)
                if corp_memb_name:
                    try:
                        corp_memb = CorporateMembership.objects.get(name=corp_memb_name)
                        membership.membership_type = corp_membi.corporate_membership_type.membership_type
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
                )

                # create entry fields
                for key, value in fields.items():

                    app_fields = AppField.objects.filter(app=app, label=key)
                    if app_fields and m.get(value):

                        try:
                            value = unicode(m.get(unicode(value)))
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
