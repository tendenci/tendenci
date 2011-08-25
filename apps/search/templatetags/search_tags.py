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
        try:
            result = self.result.resolve(context)
            result_object = result.object
            template_name = "%s/search-result.html" % (result_object._meta.app_label)
            theme = context['THEME']
            try:
                t = get_template("%s/templates/%s"%(theme,template_name))
            except TemplateDoesNotExist:
                #load the true default template directly to be sure
                #that we are not loading the active theme's template
                try:
                    t = Template(unicode(file(os.path.join(settings.PROJECT_ROOT, "templates", template_name)).read(), "utf-8"))
                except IOError:
                    t = get_template("search/search-result.html")
            context.update({
                "search_result": result,
                "search_object": result_object,
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
    context['THEME'] is used to specify a selected theme for the templates
    Example:
        {% search_result app %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("%r tag takes one argument: the search result object" % bits[0])
    return SearchResultNode(bits[1])

register.tag('search_result', search_result)
