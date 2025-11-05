import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Populate BV userID to the external_id field of profile table.
    
    Usage: python manage.py populate_bluevolt_userid
    
    """
    def handle(self, *args, **options):
        from tendenci.apps.profiles.models import Profile
        if not hasattr(settings, 'BLUEVOLT_API_KEY'):
            print('Bluevolt API is not set up. Exiting...')
            return 
        api_key = settings.BLUEVOLT_API_KEY
        api_endpoint_base_url = settings.BLUEVOLT_API_ENDPOINT_BASE_URL
        users_url = api_endpoint_base_url + '/devapi2/webapi/v2/GetAllUsers'
        headers = {'ocp-apim-subscription-key': settings.BLUEVOLT_PRIMARY_KEY}
        payload = {'apiKey': api_key ,
                   'onlyActiveUsers': 'True'}
        r = requests.get(users_url, headers=headers, params=payload)
        if r.status_code == 200:
            users_results = r.json()
            total_records = len(users_results)
            print('total=', total_records)
            for user_result in users_results:
                username = user_result['UserName']
                external_id = user_result['ID']
                if Profile.objects.filter(user__username=username,
                                         external_id=external_id).exists():
                    print(f'external_id "{external_id}" already populated.')
                    continue
                [profile] = Profile.objects.filter(user__username=username)[:1] or [None]
                if profile:
                    profile.external_id = external_id
                    profile.save(update_fields=['external_id'])
                    print(external_id)
                else:
                    print(f'user with username "{username}" does not exist.')
                