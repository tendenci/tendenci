from django import template
from pagination.templatetags.pagination_tags import paginate

register = template.Library()

register.inclusion_tag('base/bootstrap_pagination.html', takes_context=True)(
    paginate)
