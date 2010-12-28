mobile_agents = [
    'iPad',
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
    'SEJ001'
]

def is_mobile_browser(request):
    if 'HTTP_USER_AGENT' in request.META:
        full_user_agent = request.META['HTTP_USER_AGENT'].lower()
        for ma in mobile_agents:
            if ma.lower() in full_user_agent:
                return True
    return False

class MobileMiddleware(object):
    def process_request(self, request):
        request.mobile = is_mobile_browser(request)