from django.template import RequestContext


class ExceededMaxTypes(Exception):
    pass


class ExceededMaxTypesMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, ExceededMaxTypes):
            from tendenci.addons.memberships.utils import render_to_max_types
            return render_to_max_types(context_instance=RequestContext(request))
