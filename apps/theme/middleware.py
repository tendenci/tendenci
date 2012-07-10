try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

class RequestMiddleware():
    def process_request(self, request):
        _thread_locals.request = request
