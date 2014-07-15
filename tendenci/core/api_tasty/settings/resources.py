from tastypie import fields
from tendenci.core.site_settings.models import Setting

from tendenci.core.api_tasty.resources import TendenciResource
from tendenci.core.api_tasty.validation import TendenciValidation
from tendenci.core.api_tasty.settings.forms import SettingForm

class SettingResource(TendenciResource):
    """This resource will clean the given data based on the generated
    rules of the SettingForm.
    To access this resource the username and api_key of a superuser
    must be present in request.GET or request.POST
    for example,
    /api_tasty/v1/setting/1/?format=json&username=sam&api_key=6f21b5cad4841d7ba76e6d76d5b9332dddf109bf
    Note that the specification of 'format' is important.
    curl test example: (assumes you have data.json with correct file contents)
    curl -H "Content-Type: application/json" -X PUT --data @data.json "http://0.0.0.0:8000/api_tasty/v1/setting/12/?format=json&username=sam&api_key=718bdf03b2fb0f3def6e039db5cfb2a75db05f85"
    """
    name = fields.CharField(readonly=True, attribute='name')
    description = fields.CharField(readonly=True, attribute='description')

    class Meta(TendenciResource.Meta):
        queryset = Setting.objects.all()
        resource_name = 'setting'
        validation = TendenciValidation(form_class=SettingForm)
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'put']
        fields = ['name', 'description', 'value', 'data_type', 'input_value']

