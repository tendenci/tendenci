from django.template import Library, Node

# Create Django template tags for the uploader, to make it easy to add an uploader to a page.

# To use, add {% load uploader %} at the top of your template, and add {% uploader_head %} to
# {% block extra_head %} to load the js/css files needed by the uploader.  Then add
# {% uploader %}...Fine Uploader options...{% end_uploader %} in {% block content %} at the position
# where the uploader should be rendered on the page.  The "request: { endpoint: '...' }" Fine
# Uploader option must be specified to configure the URL of the Django view that will handle the
# uploads on the server.  For other options, see the Fine Uploader documentation:
# http://docs.fineuploader.com/api/options.html and http://docs.fineuploader.com/api/options-ui.html

register = Library()

@register.inclusion_tag('uploader/head.html')
def uploader_head():
    return None

class UploaderNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        template = context.template.engine.get_template('uploader/body.html')
        uploader_options = self.nodelist.render(context)
        context['uploader_options'] = uploader_options
        return template.render(context=context)

@register.tag
def uploader(parser, token):
    nodelist = parser.parse(('end_uploader',))
    parser.delete_first_token()
    return UploaderNode(nodelist)
