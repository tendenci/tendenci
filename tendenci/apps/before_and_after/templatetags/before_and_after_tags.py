from django.template import Node, Library, TemplateSyntaxError, Variable

from tendenci.apps.before_and_after.forms import SearchForm

register = Library()

@register.inclusion_tag("before_and_after/search-form.html", takes_context=True)
def before_and_after_search(context):
    context['form'] = SearchForm()
    return context
