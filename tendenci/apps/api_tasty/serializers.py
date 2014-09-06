from tastypie.serializers import Serializer

class SafeSerializer(Serializer):
    """
    Removes the optional serializers from the available formats
    to avoid dependency errors.
    """
    formats = ['json', 'jsonp', 'html']
    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
        'html': 'text/html',
    }
