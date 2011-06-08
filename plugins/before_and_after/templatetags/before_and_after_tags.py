from django.template import Node, Library, TemplateSyntaxError, Variable
from django.contrib.auth.models import AnonymousUser

from before_and_after.models import BeforeAndAfter
from before_and_after.forms import SearchForm
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()

@register.inclusion_tag("before_and_after/search-form.html", takes_context=True)
def before_and_after_search(context):
    context['form'] = SearchForm()
    return context
    
