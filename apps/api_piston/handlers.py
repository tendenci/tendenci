from piston.handler import BaseHandler
from piston.emitters import Emitter, JSONEmitter

from site_settings.models import Setting

class SettingHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Setting   
    
    def read(self, request, setting_id=None):
        base = Setting.objects
        if setting_id:
            setting = base.get(pk=setting_id)
        else:
            setting = base.all()
        return setting

Emitter.register('json', JSONEmitter, 'application/json; charset=utf-8')
