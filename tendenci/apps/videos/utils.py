from embedly import Embedly
from tendenci.apps.site_settings.utils import get_setting

ASPECT_RATIO = 1.78

def get_embedly_client():
    api_key = get_setting('module', 'videos', 'embedly_apikey')
    if not api_key:
        api_key = "438be524153e11e18f884040d3dc5c07"
    return Embedly(api_key)
