from django.utils.deprecation import MiddlewareMixin


class ExceededMaxTypes(Exception):
    pass


class ExceededMaxTypesMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, ExceededMaxTypes):
            from tendenci.apps.memberships.utils import render_to_max_types
            return render_to_max_types(request=request)
