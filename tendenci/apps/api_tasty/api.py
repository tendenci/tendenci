from django.http import HttpResponse
from tastypie.utils import is_valid_jsonp_callback_value
from tastypie.utils.mime import determine_format, build_content_type
from tastypie.api import Api
from tastypie.exceptions import BadRequest
from tendenci.apps.api_tasty.serializers import SafeSerializer

class SafeApi(Api):
    """
    Override to the tasty pie's default api to avoid errors with the
    optional libraries.
    """
    def top_level(self, request, api_name=None):
        """This is the same method in the Api model with the execption
        of the serializer used. This uses the SafeSerializer.
        """
        serializer = SafeSerializer()
        available_resources = {}

        if api_name is None:
            api_name = self.api_name

        for name in sorted(self._registry):
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
