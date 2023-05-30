import json
import requests
from django.conf import settings

from tendenci.apps.profiles.models import Profile
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.utils import adjust_datetime_to_timezone

class HigherLogicAPI:
    """
    https://support.higherlogic.com/hc/en-us/articles/360052978051-Push-API
    """
    def __init__(self):
        self.headers = {'Key': 'ApiKey', 'Value': hasattr(settings, 'HIGHERLOGIC_API_KEY') and settings.HIGHERLOGIC_API_KEY}
        self.headers = {'ApiKey': hasattr(settings, 'HIGHERLOGIC_API_KEY') and settings.HIGHERLOGIC_API_KEY}
        self.api_base_url = hasattr(settings, 'HIGHERLOGIC_API_BASE_URL') and settings.HIGHERLOGIC_API_BASE_URL

    def post_requests(self, api_url, request_data):
        #return requests.post(api_url, headers=self.headers, json=json.loads(json.dumps(request_data)))
        return requests.post(api_url, headers=self.headers, json=request_data)

    def dt_to_str(self, dt, fmt):
        """
        Convert datetime dt to UTC, then format it to a string.
        """
        if not dt:
            return ''
 
        return adjust_datetime_to_timezone(dt, settings.TIME_ZONE, 'UTC'
                                    ).strftime('%Y-%m-%dT%H:%M:%SZ') 

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
            # Security Groups -> GroupType = Membership
            groups = []
            if profile.member_number:
                groups.append(
                    {
                        "InitialJoinDate": "2015-04-19T12:25:50.537-04:00",
                        "BeginDate": "2016-06-01T00:17:25.172-04:00",
                        "EndDate": "2021-01-19T11:48:15.324-05:00",
                        "GroupId": "NCCPAPMember",
                        "GroupName": "NCCPAP Member",
                        "GroupType": "Membership",
                        "Role": ""
                      }
                    )
            
            # Community Groups -> GroupType: Chapter, Committee, Event
            request_list.append(contact_dict)
        if request_list:
            api_url = self.api_base_url + '/contactinfo'
            res = self.post_requests(api_url, request_list)
            print(res)
            return res
            
            
        
        