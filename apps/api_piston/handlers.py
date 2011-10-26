from piston.handler import BaseHandler
from piston.emitters import Emitter, JSONEmitter
from piston.utils import validate

from site_settings.models import Setting

from api_piston.forms import SettingForm

class SettingHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    model = Setting
    
    @classmethod
    def read(self, request, id=None):
        base = Setting.objects
        if id:
            setting = base.get(pk=id)
        else:
            setting = base.all()
        return setting
    
    def update(self, request, id):
        print "put"
        setting = Setting.objects.get(pk=id)
        form = SettingForm(request.POST, instance=setting)
        if form.is_valid():
            print "valid form"
            setting.value = form.cleaned_data['value']
            setting.save()
            return setting
        else:
            return {"error": form.errors}
            
    def create(self, request, id):
        print "post"
        setting = Setting.objects.get(pk=id)
        form = SettingForm(request.POST, instance=setting)
        if form.is_valid():
            print "valid form"
            setting.value = form.cleaned_data['value']
            setting.save()
            return setting
        else:
            return {"error": form.errors}
