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

def user_agent(request):
    if 'HTTP_USER_AGENT' in request.META:
        return request.META['HTTP_USER_AGENT'].lower()
    return None
    
def is_mobile_browser(request):
    if request.user_agent:
        for ma in mobile_agents:
            if ma.lower() in request.user_agent:
                return True
    return False

class MobileMiddleware(object):
    def process_request(self, request):
        request.user_agent = user_agent(request)
        request.mobile = is_mobile_browser(request)
