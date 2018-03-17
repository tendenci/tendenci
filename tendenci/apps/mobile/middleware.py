from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

mobile_agents = [
#    'iPad',  # Removed on 2012-07-11
    'iPhone',
    'iPod',
    'Android',
    'Opera Mini',
    'Blackberry',
    'Droid',
    'IEMobile',
    'EudoraWeb',
    'Fennec',
    'Minimo',
    'NetFront',
    'Polaris',
    'HTC_Dream',
    'HTC Hero',
    'HTC-ST7377',
    'Kindle',
    'LG-LX550',
    'LX265',
    'Nokia',
    'Palm',
    'MOT-V9mm',
    'SEC-SGHE900',
    'SAMSUNG-SGH-A867',
    'SymbianOS',
    'DoCoMo',
    'ZuneHD',
    'ReqwirelessWeb',
    'SEJ001',
    'SonyEricsson'
]

def user_agent(request):
    if 'HTTP_USER_AGENT' in request.META:
        return request.META['HTTP_USER_AGENT'].lower()
    return None

def is_mobile_cookie_on(request):
    cookiename =  getattr(settings, 'MOBILE_COOKIE_NAME', "tendenci_mobile")
    if cookiename in request.COOKIES:
        if request.COOKIES[cookiename] == "0":
            return False
    return True

def is_mobile_browser(request):
    if request.user_agent:
        for ma in mobile_agents:
            if ma.lower() in request.user_agent:
                return True
    return False

def show_mobile(request):
    if not is_mobile_cookie_on(request):
        # no need to check any further, the user opt-out
        return False

    if is_mobile_browser(request):
        return True
    return False


class MobileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user_agent = user_agent(request)
        request.mobile_browser = is_mobile_browser(request)
        request.mobile = show_mobile(request)
