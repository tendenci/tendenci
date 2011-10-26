from django.conf.urls.defaults import *

from piston.resource import Resource

class CsrfExemptResource(Resource):
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)

from api_piston.handlers import SettingHandler

setting_handler = CsrfExemptResource(SettingHandler)

urlpatterns = patterns('',
    url(r'^settings/(?P<id>\d+)/$', setting_handler),
    url(r'^settings/$', setting_handler),
)
