import os
from datetime import datetime
from dateutil.parser import parse as dt_parse
from django.contrib.auth.models import User
from django.conf import settings
from celery.task import Task
from profiles.models import Profile
from corporate_memberships.models import CorporateMembership
from memberships.models import AppEntry, AppField, AppFieldEntry, MembershipType, Membership
from memberships.importer.utils import parse_mems_from_csv, clean_field_name


class ImportMembershipsTask(Task):

    def run(self, memport, fields, **kwargs):
        from django.template.defaultfilters import slugify
        from memberships.utils import get_user

        app = memport.app
        file_path = os.path.join(settings.MEDIA_ROOT, memport.get_file().file.name)

        #get parsed membership dicts
        imported = []
        mems, stats = parse_mems_from_csv(
            file_path,
            fields,
            membership_import=memport
        )

        for m in mems:
            if not m['skipped']:
                # membership type exists; we have tested; can add more tests here
                membership_type = MembershipType.objects.get(name=m['membershiptype'])

                # initialize dates
                expire_dt = m['expiredt']
                subscribe_dt = m['subscribedt']

                payment_methods = {
                    'cc': 1,
                    'credit': 1,
                    'credit card': 1,
                    'check': 2,
                    'cash': 3
                }

                # get payment method id; assumes default payment methods
                payment_method = slugify(m.get('paymentmethod', '')).replace('-', '')
                payment_method_id = payment_methods.get(payment_method)

                user = get_user(username=m['username'])

                if not user:
                    if m['username'] and m['email']:
                        user = User.objects.create_user(m['username'], m['email'])

                # get or create profile
                try:
                    profile = Profile.objects.get(user=user)
                except Profile.MultipleObjectsReturned:
                    profile = Profile.objects.filter(user=user)[0]
                except Profile.DoesNotExist:
                    profile = Profile.objects.create_profile(user)

                if memport.override:
                    user.first_name = m.get('firstname', '') or user.first_name
                    user.last_name = m.get('lastname', '') or user.last_name
                    user.email = m['email'] or user.email
                    profile.company = m.get('company', '') or profile.company
                    profile.position_title = m.get('positiontitle', '') or profile.position_title
                    profile.address = m.get('mailingaddress', '') or profile.address
                    profile.address2 = m.get('address2', '') or profile.address2
                    profile.city = m.get('city', '') or profile.city
                    profile.state = m.get('state', '') or profile.state
                    profile.zipcode = m.get('zipcode', '') or profile.zipcode
                    profile.county = m.get('county', '') or profile.county
                    profile.address_type = m.get('addresstype', '') or profile.address_type
                    profile.work_phone = m.get('workphone', '') or profile.work_phone
                    profile.home_phone = m.get('homephone', '') or profile.home_phone
                    profile.mobile_phone = m.get('mobilephone', '') or profile.mobile_phone
                    profile.email = user.email
                    profile.email2 = m.get('email2', '') or profile.email2
                    profile.url = m.get('website', '') or profile.url
                    profile.dob = dt_parse(m.get('dob', ''))
                else:
                    user.first_name = user.first_name or m['firstname']
                    user.last_name = user.last_name or m['lastname']
                    user.email = user.email or m['email']
                    profile.company = profile.company or m.get('company', '')
                    profile.position_title = profile.position_title or m.get('positiontitle', '')
                    profile.address = profile.address or m.get('mailingaddress', '')
                    profile.address2 = profile.address2 or m.get('address2', '')
                    profile.city = profile.city or m.get('city', '')
                    profile.state = profile.state or m.get('state', '')
                    profile.zipcode = profile.zipcode or m.get('zipcode', '')
                    profile.country = profile.county or m.get('county', '')
                    profile.address_type = profile.address_type or m.get('addresstype', '')
                    profile.work_phone = profile.work_phone or m.get('workphone', '')
                    profile.home_phone = profile.home_phone or m.get('homephone', '')
                    profile.mobile_phone = profile.mobile_phone or m.get('mobilephone', '')
                    profile.email = user.email or m.get('email', '')
                    profile.email2 = profile.email2 or m.get('email2', '')
                    profile.url = profile.url or m.get('website', '')
                    profile.dob = profile.dob or dt_parse(m.get('dob', ''))

                user.save()
                profile.save()

                # get or create membership
                # relation does not hold unique constraints
                # so we assume the first hit is the correct membership
                # if it exists.
                memberships = Membership.objects.filter(
                    user=user,
                    membership_type=membership_type,
                )  # oldest on top

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

                membership.save()  # update_dt changes

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

                entry = membership.get_entry()

                if not entry:
                    entry = AppEntry.objects.create(
                        app=app,
                        user=membership.user,
                        entry_time=datetime.now(),
                        membership=membership,  # pk required here
                        is_renewal=membership.renewal,
                        is_approved=True,
                        decision_dt=membership.subscribe_dt,
                        judge=membership.creator,
                        creator=membership.creator,
                        creator_username=membership.creator_username,
                        owner=membership.owner,
                        owner_username=membership.owner_username,
                        allow_anonymous_view=False,
                    )

                entry_dict = {}  # entry pk and value
                field_dict = {}
                for field in entry.fields.all():
                    entry_dict[field.field.label] = {
                        'item': field,
                        'field': field.field,
                        'value': field.value.strip()
                        }
                    field_dict[field.field.label] = field.field

                # get a concise list of all app fields
                app_fields = AppField.objects.filter(app=app)
                for field in app_fields:

                    entry_field = entry_dict.get(field.label, {})

                    entry_dict[field.label] = {
                        'item': entry_field.get('item'),  # default: None
                        'field': entry_field.get('field'),  # default: None
                        'value': entry_field.get('value', u'').strip()
                    }
                    field_dict[field.label] = field

                # [finally] loop through all entry items
                # setting values from csv and saving entry items
                for k, d in entry_dict.items():

                    entry_item = d['item'] or AppFieldEntry()
                    field_name = clean_field_name(k).replace('_', '').strip()
                    imported_value = m.get(field_name, u'').strip()

                    if not entry_item.pk:
                        entry_item.entry = entry
                        entry_item.field = field_dict[k]

                    if memport.override:
                        # update all fields (if csv has value)
                        entry_item.value = imported_value or d['value']
                    else:
                        # update blank fields
                        entry_item.value = d['value'] or imported_value

                    # save will either create or update
                    # depending if a pk is available
                    entry_item.save()

                print m['memberid']

                # update membership number
                if not membership.member_number:
                    membership.member_number = AppEntry.objects.count() + 1000
                    membership.save()

                # add user to group
                membership.membership_type.group.add_user(membership.user)

                # append to imported list
                imported.append(membership)

        return imported, stats
