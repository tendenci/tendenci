import base64
import requests

# from django.conf import settings


DEFAULT_BASE_URL = "https://api.zoom.us/v2"
TOKEN_URL = "https://zoom.us/oauth/token"


class ZoomSession(requests.Session):
    """
    Use requests.Session to access Zoom API
    """
    PATH = "{base_url}{endpoint}"

    def __init__(
            self,
            client_id,
            client_secret,
            account_id,
            base_url=DEFAULT_BASE_URL,
            token_url=TOKEN_URL
    ):
        super().__init__()
        self.base_url = base_url
        self.__authenticate(client_id, client_secret, account_id, token_url)

    def __authenticate(self, client_id, client_secret, account_id, token_url):
        """
        Authenticate by getting OAuth Token
        """
        headers = {
            "Authorization": "Basic "
            + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {'account_id': account_id, 'grant_type': 'account_credentials'}

        response = requests.post(token_url, headers=headers, data=data)

        token = response.json().get('access_token')
        self.headers = {'Authorization': f'Bearer {token}'}

    def prepare_request(self, request):
        """
        Update request with base URL
        """
        request.url = self.PATH.format(base_url=self.base_url, endpoint=request.url)

        return super().prepare_request(request)


class ZoomClient(ZoomSession):
    """Access endpoints to pull Zoom meeting information"""
    MEETINGS = "/meetings/{meeting_id}"
    MEETING_POLLS = "/meetings/{meeting_id}/polls"
    MEETING_POLL_RESULTS = "/past_meetings/{meeting_id}/polls"
    WEBINAR_POLL_RESULTS = "/past_webinars/{webinar_id}/polls"
    WEBINAR_POLLS = "/webinars/{webinar_id}/polls"

    def get_meeting(self, meeting_id):
        return self.get(self.MEETINGS.format(meeting_id=meeting_id))

    def get_meeting_polls(self, meeting_id, is_webinar=False):
        if is_webinar:
            return self.get_webinar_poll_results(meeting_id)
        return self.get(self.MEETING_POLLS.format(meeting_id=meeting_id))

    def get_meeting_poll_results(self, meeting_id, is_webinar=False):
        if is_webinar:
            return self.get_webinar_poll_results(meeting_id)
        return self.get(self.MEETING_POLL_RESULTS.format(meeting_id=meeting_id))

    def get_webinar_polls(self, webinar_id):
        return self.get(self.WEBINAR_POLLS.format(webinar_id=webinar_id))

    def get_webinar_poll_results(self, webinar_id):
        return self.get(self.WEBINAR_POLL_RESULTS.format(webinar_id=webinar_id))
