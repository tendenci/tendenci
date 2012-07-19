from django.template import Node, Library, TemplateSyntaxError, Variable

from chamberlin_projects.models import Project
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListProjectsNode(ListNode):
    model = Project
    perms = 'chamberlin_projects.view_project'


@register.tag
def list_chamberlin_projects(parser, token):
    """
    Example:

    {% list_chamberlin_projects as chamberlin_projects_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for project in chamberlin_projects %}
        {{ project.something }}
    {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires more than 2" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListProjectsNode(context_var, *args, **kwargs)

@register.inclusion_tag("chamberlin_projects/search-form.html", takes_context=True)
def project_search(context):
    return context
