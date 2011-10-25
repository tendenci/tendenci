from tastypie.serializers import Serializer

class SafeSerializer(Serializer):
    """
    I should not need to create this but
    for some reason the default format is always xml
    which triggers errors because that lib is optional.
    """
    formats = ['json', 'jsonp', 'html']
    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
        'html': 'text/html',
    }
