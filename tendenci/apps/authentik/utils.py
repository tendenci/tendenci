import requests
import json

from django.conf import settings

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.emails.models import Email
from .models import AuthentikUserMapping


class AuthentikAPI:
    """
    https://api.goauthentik.io/
    https://api.goauthentik.io/reference/core-users-create/
    """
    def __init__(self):
        authorization = f'Bearer {settings.AUTHENTIK_TOKEN}'
        self.headers_for_get = {
              'Accept': 'application/json',
              'Authorization': authorization,
            }
        self.headers_for_post = {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
              'Authorization': authorization,
            }
        self.headers_for_post2 = {
              'Content-Type': 'application/json',
              'Authorization': authorization,
            }
        self.headers_for_delete = {
              'Authorization': authorization,
            }
        self.api_base_url = settings.AUTHENTIK_BASE_URL


    def process_response(self, res, success_status_code=200):
        # success_status_code
        # 204 - DELETE
        # 201 - POST
        # 200 - PUT, GET
        if not res.ok or res.status_code != success_status_code:
            self.email_support_errors(res.text)
        #print(res)
        return res

    def push_user_to_authentik(self, user):
        """
        Check and push user to authentik.
        """
        # check if already pushed
        if AuthentikUserMapping.objects.filter(user_id=user.id).exists():
            # if already saved on site, do nothing
            return 'Already pushed to authentik', None
        
        # Check if this user is an active member
        membership = user.membershipdefault_set.filter(
                    status_detail__iexact='active', status=True
                    ).order_by('-create_dt').first()
        if not membership:
            return f'user {user} is not an active member', None

        if not user.email:
            return f'user {user} has NO email address', None
    
        # TODO: check if this user already on Authentik
        
        # create user on authentik
        url = self.api_base_url + 'core/users/'
        # other fields - groups, roles, path, type..
        payload = json.dumps({
            'username': user.username,
            'name': user.get_full_name(),
            "email": user.email,
            'type': 'external',
            "is_active": True})
        response = requests.request("POST", url, headers=self.headers_for_post, data=payload)
        self.process_response(response, 201)
        print('Pushing to authentik ... response.status_code =', response.status_code)
        print(response.text)
        # status_code: 500, 201 (created)
        if response.status_code == 201:
            try:
                au_mapping = self.save_authentik_user_id(response, user)
            except json.decoder.JSONDecodeError:
                print(response.text)
                return response.text, None
            return 'Added', au_mapping
        if response.status_code == 400:
            msg_dict = json.loads(response.text)
            print(msg_dict['non_field_errors'])
            return 'Error', None
        return response.status_code, None

    def save_authentik_user_id(self, response, user):
        user_dict = json.loads(response.text)
        if 'pk' not in user_dict:
            print(user_dict)
            return
        a_user_id = user_dict['pk']
        if not AuthentikUserMapping.objects.filter(user_id=user.id, a_user_id=a_user_id).exists():
            au_mapping = AuthentikUserMapping.objects.create(user_id=user.id, a_user_id=a_user_id)
            return au_mapping
        # pass the hashed password to authentik, so user can log in on authentik
        # comment it out - this API call returns 405 "Method Not Allowed"
        # url = self.api_base_url + f'core/users/{a_user_id}/set_password_hash/'
        # payload = json.dumps({
        #     'password': user.password
        #     })
        # response = requests.request("POST", url, headers=self.headers_for_post, data=payload)
        # self.process_response(response, 204)

    def remove_user(self, user_id):
        au_mapping = AuthentikUserMapping.objects.filter(user_id=user_id).first()
        if au_mapping:
            a_user_id = au_mapping.a_user_id
            url = self.api_base_url + f'core/users/{a_user_id}/'
            response = requests.request("DELETE", url, 
                                        headers=self.headers_for_delete, 
                                        data={})
            self.process_response(response, 204)
            if response.status_code == 204:
                au_mapping.delete()

    def email_support_errors(self, error_message):
        """if there is an error other than transaction not being approved, notify us.
        """
        admins = getattr(settings, 'ADMINS', None)
        if admins:
            recipients_list = [admin[1] for admin in admins]
            email = Email()
            email.recipient = ','.join(recipients_list)
            site_url = get_setting('site', 'global', 'siteurl')
            email.subject = 'Error pushing data to Authentik'
            email.body = 'An error occurred while pushing data to Authentik.\n\n'
            email.body += error_message
            email.body += '\n\n'
            email.body += f'Website: {site_url}'
            email.content_type = "text"
            email.priority = 1