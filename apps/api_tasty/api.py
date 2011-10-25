from tastypie.resources import ModelResource
from site_settings.models import Setting
from tastypie.serializers import Serializer

#class JSONSerializer(Serializer):
#    """
#    I should not need to create this but
#    for some reason the default format is always xml.
#    """
#    formats = ['json']
#    content_types = {
#        'json': 'application/json',
#    }

class SettingResource(ModelResource):
    class Meta:
        queryset = Setting.objects.all()
