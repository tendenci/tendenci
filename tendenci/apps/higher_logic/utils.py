import requests
import re
from datetime import datetime, timezone, timedelta
import pprint
import phonenumbers

from django.conf import settings
from django.db.models import Q

from tendenci.apps.profiles.models import Profile
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.user_groups.models import GroupMembership
from tendenci.apps.events.models import Registrant, AssetsPurchase
from tendenci.apps.staff.models import Staff
from tendenci.apps.emails.models import Email


class HigherLogicAPI:
    """
    https://support.higherlogic.com/hc/en-us/articles/360052978051-Push-API
    """
    def __init__(self):
        self.headers = {'Key': 'ApiKey', 'Value': hasattr(settings, 'HIGHERLOGIC_API_KEY') and settings.HIGHERLOGIC_API_KEY}
        self.headers = {'ApiKey': hasattr(settings, 'HIGHERLOGIC_API_KEY') and settings.HIGHERLOGIC_API_KEY}
        self.api_base_url = hasattr(settings, 'HIGHERLOGIC_API_BASE_URL') and settings.HIGHERLOGIC_API_BASE_URL
        # Alpha-2 code country code only
        # ToDo: Include more countries 
        self.country_code_d = {'United States': 'US',
                          'United States of America': 'US',
                          'US': 'US', 
                          'Canada': 'CA',
                          'Mexico': 'MX'}

    def post_requests(self, api_url, request_data):
        return requests.post(api_url, headers=self.headers, json=request_data)

    def process_response(self, res):
        if not res.ok or res.status_code != 200:
            self.email_support_errors(res.text)
        #print(res)
        return res

    def dt_isoformat(self, dt):
        """
        Convert datetime dt to UTC iso 8601 format.
        """
        return dt and dt.astimezone(timezone.utc).isoformat('T', 'milliseconds').replace('+00:00', 'Z')

    def get_user_member_group(self, profile):
        """
        Get member group dict for profile.user. Member group is a security group
        """
        member_group = None
        if profile.member_number:
            # member group
            membership = profile.membership
            if membership:
                member_group = {"GroupId": get_setting('module', 'higher_logic', 'membergroupkey'),
                                "GroupName": get_setting('module', 'higher_logic', 'membergroupname'),
                                "GroupType": "Membership",
                                "Role": ""} # membership type?
                if membership.join_dt:
                    member_group['InitialJoinDate'] = self.dt_isoformat(membership.join_dt)
                if membership.renewal and membership.renew_dt:
                    member_group['BeginDate'] = self.dt_isoformat(membership.renew_dt)
                else:
                    # join
                    if 'InitialJoinDate' in member_group:
                        member_group['BeginDate'] = member_group['InitialJoinDate']
                if membership.expire_dt:
                    member_group['EndDate'] = self.dt_isoformat(membership.expire_dt)
        return member_group

    def get_user_staff_group(self, user):
        """
        Get staff group dict for user. Staff group is also a security group.
        """
        [staff] = Staff.objects.filter(user=user).filter(status=True, status_detail='active')[:1] or [None]
        if staff:
            return {"GroupId": get_setting('module', 'higher_logic', 'staffgroupkey'),
                   "GroupName": get_setting('module', 'higher_logic', 'staffgroupname'),
                   "GroupType": "Membership",
                   "Role": ""}
        return None

    def get_user_community_groups(self, user):
        """
        Get a list of community groups dict. Community groups include Chapter, Committee and Event
        """
        community_groups = []
        now = datetime.now()
        group_memberships = GroupMembership.objects.filter(
                                    member=user,
                                    status=True,
                                    status_detail=GroupMembership.STATUS_ACTIVE)
        for group_membership in group_memberships:
            group = group_membership.group

            # chapter - unique identifier is: chapter-[id] (where [id] is the value of the chapter id field
            [chapter] = group.chapter_set.filter(status_detail='active', status=True)[:1] or [None]
            if chapter:
                pass
                # [officer] = chapter.officer_set.filter(user=user).filter(Q(expire_dt__isnull=True) | Q(expire_dt__gt=now))[:1] or [None]
                # community_groups.append({"GroupId": f'chapter-{chapter.id}',
                #     "GroupName": chapter.title,
                #     "GroupType": "Chapter",
                #     "Role": officer and officer.position.title or ''})

            else:
                # committee - unique identifier is: committee-[id] (where [id] is the value of the committee id field
                [committee] = group.committee_set.filter(status_detail='active', status=True)[:1] or [None]
                if committee:
                    [officer] = committee.officer_set.filter(user=user).filter(Q(expire_dt__isnull=True) | Q(expire_dt__gt=now))[:1] or [None]
                    community_groups.append({"GroupId": f'committee-{committee.id}',
                        "GroupName": committee.title,
                        "GroupType": "Committee",
                        "Role": officer and officer.position.title or ''})
        
        # event registrations - unique identifier is: event-[id] (where [id] is the value of the event id field
        regs = Registrant.objects.filter(user=user, cancel_dt__isnull=True)
        for registrant in regs:
            reg8n = registrant.registration 
            event = reg8n.event
            # skip the past events
            #if event.start_dt > now - timedelta(days=1): 
            if event.registration_configuration.enabled:
                community_groups.append({"GroupId": f'event-{event.id}',
                    "GroupName": event.title,
                    "GroupType": "Event",
                    "Role": ''})

        #   AssetsPurchase
        assets_purchases = AssetsPurchase.objects.filter(user=user)
        for assets_purchase in assets_purchases:
            if assets_purchase.status_detail == 'approved':
                event = assets_purchase.event
                community_groups.append({"GroupId": f'event-{event.id}',
                        "GroupName": event.title,
                        "GroupType": "Event",
                        "Role": ''})
        
        return community_groups

    def get_user_address_list(self, profile):
        """
        Get user address list
        """
        addresses = []
        if profile.address or profile.city or profile.state:
            addresses.append({
                    "AddressLine1": profile.address,
                    "AddressLine2": profile.address2,
                    "City": profile.city,
                    "StateProvince": profile.state,
                    "PostalCode": profile.zipcode,
                    "CountryCode": self.country_code_d.get(profile.country, ''),
                    "AddressType": "Main",
                    "DoNotPublish": profile.hide_in_search,
                    "IsBill": profile.is_billing_address,
                    "IsPrimary": True
                  })
        if profile.address_2 or profile.city_2 or profile.state_2:
            addresses.append({
                    "AddressLine1": profile.address_2,
                    "AddressLine2": profile.address2_2,
                    "City": profile.city_2,
                    "StateProvince": profile.state_2,
                    "PostalCode": profile.zipcode_2,
                    "CountryCode": self.country_code_d.get(profile.country_2, ''),
                    "AddressType": "Main",
                    "DoNotPublish": profile.hide_in_search,
                    "IsBill": profile.is_billing_address_2,
                    "IsPrimary": False
                  })
        return addresses  

    def format_phone_number(self, phone):
        """
        The required format is: xxx-xxx-xxxx.
        """
        p = re.compile(r'\d{3}-\d{3}-\d{4}')
        if p.search(phone):
            return phone

        p2 = re.compile(r'\((\d{3})\) (\d{3}-\d{4})')
        match = p2.search(phone)
        if match:
            return f'{match.group(1)}-{match.group(2)}'

        try:
            x = phonenumbers.parse(phone, 'US')
        except phonenumbers.phonenumberutil.NumberParseException:
            return phone
 
        formatted_phone = phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.NATIONAL)
        match = p2.search(formatted_phone)
        if match:
            return f'{match.group(1)}-{match.group(2)}'

        return phone

    def get_user_phone_list(self, profile):
        """
        Get user phone list
        """
        phones = []
        if profile.phone:
            phones.append({
                    "FormattedNumber": self.format_phone_number(profile.phone),
                    "PhoneType": "Main Phone",
                    "IsPreferred": True,
                    "DoNotPublish": profile.hide_phone
                  })
        if profile.work_phone:
            phones.append({
                    "FormattedNumber": self.format_phone_number(profile.work_phone),
                    "PhoneType": "Work",
                    "IsPreferred": True,
                    "DoNotPublish": profile.hide_phone
                  })
        if profile.home_phone:
            phones.append({
                    "FormattedNumber": self.format_phone_number(profile.home_phone),
                    "PhoneType": "Home",
                    "IsPreferred": True,
                    "DoNotPublish": profile.hide_phone
                  })
        if profile.mobile_phone:
            phones.append({
                    "FormattedNumber": self.format_phone_number(profile.mobile_phone),
                    "PhoneType": "Mobile",
                    "IsPreferred": True,
                    "DoNotPublish": profile.hide_phone
                  })
        return phones

    def get_user_email_list(self, profile):
        """
        Get user email list
        """
        emails = []
        if profile.user.email:
            emails.append({
                "EmailAddress": profile.user.email,
                "EmailType": "Primary Email",
                "IsPreferred": True,
                "DoNotPublish": profile.hide_email
              })
        if profile.email2:
            emails.append({
                "EmailAddress": profile.email2,
                "EmailType": "Secondary Email",
                "DoNotPublish": profile.hide_email
              })
        return emails

    def push_user_info(self, users_list):
        """
        Push one or more users info via /contactinfo endpoint
        """
        request_list = []
        site_url = get_setting('site', 'global', 'siteurl')
        
        for user in users_list:
            if hasattr(user, 'profile'):
                profile = user.profile
            else:
                profile = Profile.objects.create_profile(user=user)

            if not profile.account_id:
                continue

            photo_url = profile.get_photo_url()
            if photo_url:
                photo_url = site_url + photo_url
            
            contact_dict = {'ContactDetails': {
                            'ContactId': str(profile.account_id),
                            'FirstName': user.first_name,
                            'LastName': user.last_name,
                            'PrimaryEmailAddress': user.email,
                            'Gender': profile.sex or '',
                            'Prefix': profile.salutation or '',
                            'OrganizationName': profile.company or '',
                            'Title': profile.position_title or '',
                            'DoNotEmail': not profile.direct_mail,
                            'IsMember': profile.member_number is not None and profile.member_number != '',
                            'IsOrganization': False,
                            'WebsiteURL': profile.url or '',
                            'ProfileImageURL': photo_url or '',
                            'FacebookURL': profile.facebook or '',
                            'TwitterURL': profile.twitter or '',
                            'LinkedinURL': profile.linkedin or '',
                            'IsDeleted': False
                            }}
            if profile.dob:
                contact_dict['ContactDetails']['Birthday'] = self.dt_isoformat(profile.dob)

            # Security Groups -> GroupType = Membership
            #        1) Member group 2) Staff group
            groups = []
            member_group = self.get_user_member_group(profile)
            if member_group:
                groups.append(member_group)

            # staff group
            staff_group = self.get_user_staff_group(user)
            if staff_group:
                groups.append(staff_group)

            # Community Groups -> GroupType: Chapter, Committee, Event

            community_groups = self.get_user_community_groups(user)
            if community_groups:
                groups.extend(community_groups)

            # add Groups to the contact_dict
            if groups:
                contact_dict['Groups'] = groups

            # Demographics

            # Education # No need to push to HL
            # JobHistory # we don't have it in Tendenci

            # Addresses
            address_list = self.get_user_address_list(profile)
            if address_list:
                contact_dict['Addresses'] = address_list

            # PhoneNumbers
            phone_list = self.get_user_phone_list(profile)
            if phone_list:
                contact_dict['PhoneNumbers'] = phone_list

            # EmailAddresses
            email_list = self.get_user_email_list(profile)
            if email_list:
                contact_dict['EmailAddresses'] = email_list

            request_list.append(contact_dict)

        #pprint.pprint(request_list)
        if request_list:
            api_url = self.api_base_url + '/contactinfo'
            res = self.post_requests(api_url, request_list)
            self.process_response(res)
            return res

    def remove_user(self, account_id):
        request_list = [{'ContactDetails': {
                            'ContactId': str(account_id),
                            'IsDeleted': True
                        }}]
        api_url = self.api_base_url + '/contactinfo'
        res = self.post_requests(api_url, request_list)
        self.process_response(res)
              
    def push_events(self, events_list):
        """
        Push one or more events (meetings) via /meeting endpoint
        """
        request_list = []
        for event in events_list:
            if event.parent:
                # skip sub events
                continue

            if event.status_detail != 'active':
                # skip non-active events
                continue

            event_dict = {
                "MeetingId": f'event-{event.id}',
                "Title": event.title,
                "Description": event.description,
                "MeetingType": event.type and event.type.name,
                "BeginDate": self.dt_isoformat(event.start_dt),
                "EndDate": self.dt_isoformat(event.end_dt),
                }
            if event.timezone:
                event_dict['TimeZone'] = event.timezone.key
            reg_conf = event.registration_configuration
            if reg_conf.enabled:
                reg_start_dt = event.reg_start_dt()
                if reg_start_dt:
                    event_dict['RegistrationOpenDate'] = self.dt_isoformat(reg_start_dt)
                reg_end_dt = event.reg_end_dt()
                if reg_end_dt:
                    event_dict['RegistrationCloseDate'] = self.dt_isoformat(reg_end_dt)
            
            prices_list = reg_conf.regconfpricing_set.filter(
                    Q(allow_anonymous=True) | \
                    Q(allow_user=True) | \
                    Q(allow_member=True)).values_list('price', flat=True)
            if prices_list:
                prices_list = [str(price) for price in prices_list]
                event_dict['Price'] = ', '.join(prices_list)
            if event.place:
                event_dict['LocationName'] = event.place.name
                if event.place.address:
                    event_dict['AddressLine1'] = event.place.address
                if event.place.city:
                    event_dict['City'] = event.place.city
                if event.place.state:
                    event_dict['State'] = event.place.state
                if event.place.zip:
                    event_dict['PostalCode'] = event.place.zip
                if event.place.address:
                    event_dict['Country'] = self.country_code_d.get(event.place.country, '')
            request_list.append(event_dict)

        #pprint.pprint(request_list)
        if request_list:
            api_url = self.api_base_url + '/meeting'
            res = self.post_requests(api_url, request_list)
            self.process_response(res)

    def remove_event(self, identifier):
        request_list = [{'MeetingId': identifier,
                        'IsDeleted': True
                        }]
        api_url = self.api_base_url + '/meeting'
        res = self.post_requests(api_url, request_list)
        self.process_response(res)
   
    def email_support_errors(self, error_message):
        """if there is an error other than transaction not being approved, notify us.
        """
        admins = getattr(settings, 'ADMINS', None)
        if admins:
            recipients_list = [admin[1] for admin in admins]
            email = Email()
            email.recipient = ','.join(recipients_list)
            site_url = get_setting('site', 'global', 'siteurl')
            email.subject = 'Error pushing data to Higher Logic'
            email.body = 'An error occurred while pushing data to Higher Logic.\n\n'
            email.body += error_message
            email.body += '\n\n'
            email.body += f'Website: {site_url}'
            email.content_type = "text"
            email.priority = 1
