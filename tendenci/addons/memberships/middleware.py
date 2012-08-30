from django.template import RequestContext
from tendenci.addons.memberships.utils import ExceededMaxTypes, render_to_max_types

class ExceededMaxTypesMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, ExceededMaxTypes):
            return render_to_max_types(context_instance=RequestContext(request))