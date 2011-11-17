from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core.cache import cache
from django.core.files import File

from tastypie.exceptions import NotRegistered
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash, is_valid_jsonp_callback_value
from tastypie.utils.mime import determine_format, build_content_type

from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.api import Api
from tastypie import fields

from site_settings.models import Setting
from site_settings.utils import delete_setting_cache, cache_setting, delete_all_settings_cache
from site_settings.cache import SETTING_PRE_KEY
from discounts.models import Discount
from api_tasty.resources import BetterModelResource
from api_tasty.serializers import SafeSerializer
from api_tasty.forms import SettingForm
from api_tasty.auth import DeveloperApiKeyAuthentication
from api_tasty.validation import ModelFormValidation

class SafeApi(Api):
    """
    Override to the tasty pie's default api to avoid errors with the
    optional libraries.
    """
    def top_level(self, request, api_name=None):
        """
        A view that returns a serialized list of all resources registers
        to the ``Api``. Useful for discovery.
        """
        serializer = SafeSerializer()
        available_resources = {}
        
        if api_name is None:
            api_name = self.api_name
        
        for name in sorted(self._registry.keys()):
            available_resources[name] = {
                'list_endpoint': self._build_reverse_url("api_dispatch_list", kwargs={
                    'api_name': api_name,
                    'resource_name': name,
                }),
                'schema': self._build_reverse_url("api_get_schema", kwargs={
                    'api_name': api_name,
                    'resource_name': name,
                }),
            }
        
        desired_format = determine_format(request, serializer)
        options = {}
        
        if 'text/javascript' in desired_format:
            callback = request.GET.get('callback', 'callback')
            
            if not is_valid_jsonp_callback_value(callback):
                raise BadRequest('JSONP callback name is invalid.')
            
            options['callback'] = callback
        
        serialized = serializer.serialize(available_resources, desired_format, options)
        return HttpResponse(content=serialized, content_type=build_content_type(desired_format))

class SettingResource(BetterModelResource):
    """
    This resource will clean the given data based on the generated
    rules of the SettingForm.
    To access this resource the username and api_key of a developer
    must be present in request.GET or request.POST
    for example,
    /api_tasty/v1/setting/1/?format=json&username=user&api_key=1191910191019101
    Note that the specification of 'format' is important.
    curl test example: (assumes you have data.json with correct file contents)
    curl -H "Content-Type: application/json" -X PUT --data @data.json "http://0.0.0.0:8000/api_tasty/v1/setting/12/?format=json&username=user&api_key=1191910191019101"
    """
    name = fields.CharField(readonly=True, attribute='name')
    description = fields.CharField(readonly=True, attribute='description')
    
    def __init__(self, *args, **kwargs):
        super(SettingResource, self).__init__(*args, **kwargs)
    
    class Meta:
        queryset = Setting.objects.all()
        resource_name = 'setting'
        serializer = SafeSerializer()
        authorization = Authorization()
        authentication = DeveloperApiKeyAuthentication()
        fields = ['name', 'description', 'value', 'data_type', 'input_value']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'put']
        validation = ModelFormValidation(form_class=SettingForm)
        
class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        serializer = SafeSerializer()
        authorization = Authorization()
        authentication = DeveloperApiKeyAuthentication()
        fields = ['username', 'first_name', 'last_name']
        allowed_methods = ['get']
        
class DiscountResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner')
    creator = fields.ForeignKey(UserResource, 'creator')
    class Meta:
        queryset = Discount.objects.all()
        resource_name = 'discount'
        serializer = SafeSerializer()
        authorization = Authorization()
        authentication = DeveloperApiKeyAuthentication()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
