from django import template
from dj_pagination.templatetags.pagination_tags import paginate, do_autopaginate

register = template.Library()

register.inclusion_tag('base/bootstrap_pagination.html', takes_context=True)(
    paginate)
register.tag('autopaginate', do_autopaginate)
