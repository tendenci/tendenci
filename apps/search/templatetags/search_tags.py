import os
from django.template import TemplateSyntaxError, TemplateDoesNotExist, Variable
from django.template import Library, Template
from django.conf import settings
from django.template.loader import get_template
from django.template.loader_tags import ExtendsNode, IncludeNode, ConstantIncludeNode

register = Library()

class SearchResultNode(IncludeNode):
    def __init__(self, result):
        self.result = Variable(result)
    
    def render(self, context):
        """
        This does not take into account preview themes.
        """
        try:
            result = self.result.resolve(context)
            try:
                result_object = result.object
            except:
                result_object = result
            var_name = result_object._meta.verbose_name.replace(' ', '_').lower()
            if var_name == 'user':
                # special case for users and profiles
                var_name = 'profile'

            if var_name == 'photo_set':
                #special case since Image and PhotoSet share the same app.
                template_name = "photos/photo-set/search-result.html"
            else:
                template_name = "%s/search-result.html" % (result_object._meta.app_label)
            try:
                t = get_template(template_name)
            except TemplateDoesNotExist:
                #load the default search result template
                t = get_template("search/search-result.html")
                
            context.update({
                "result": result,
                var_name: result_object,
            })
            return t.render(context)
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''

def search_result(parser, token):
    """
    Loads the search-result.html and renders it with the current context
    and the given app name.
    {% search_result app %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("%r tag takes one argument: the search result object" % bits[0])
    return SearchResultNode(bits[1])

register.tag('search_result', search_result)
