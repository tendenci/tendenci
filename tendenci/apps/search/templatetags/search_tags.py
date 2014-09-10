import os
from django.template import TemplateSyntaxError, TemplateDoesNotExist, Variable
from django.template import Library, Template
from django.conf import settings
from django.template.loader import get_template
from django.template.loader_tags import ExtendsNode, IncludeNode, ConstantIncludeNode
from django.utils.translation import ugettext_lazy as _

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

            if hasattr(result, 'object'):
                result_object = result.object
            else:
                result_object = result

            if not result_object:
                return u''

            var_name = result_object._meta.verbose_name.replace(' ', '_').lower()

            # class_name is static - it won't be changed by the user
            class_name = result_object.__class__.__name__.lower()
            if class_name == 'corporatemembership':
                var_name = 'corporate_membership'
                #template_name = "corporate_memberships/search-result.html"
            if class_name == 'membership':
                var_name = 'membership'

            if var_name == 'user':
                # special case for users and profiles
                var_name = 'profile'
            if var_name == 'member':
                var_name = 'membership'
            if var_name == 'corporate_member':
                var_name = 'corporate_membership'
            if var_name == 'photo':
                var_name = 'photo_set'
            if var_name == 'photo_album':
                #special case since Image and PhotoSet share the same app.
                var_name = 'photo_set'
                template_name = "photos/photo-set/search-result.html"
            elif var_name == 'application_entry':
                var_name = 'entry'
                template_name = "memberships/entries/search-result.html"
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
        raise TemplateSyntaxError(_("%(bit)r tag takes one argument: the search result object" % {'bit':bits[0]}))
    return SearchResultNode(bits[1])

register.tag('search_result', search_result)
