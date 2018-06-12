from django.template import Node, Library, TemplateSyntaxError, Variable

from tendenci.apps.projects.models import Project
from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListProjectsNode(ListNode):
    model = Project
    perms = 'projects.view_project'


@register.inclusion_tag("projects/top_nav_items.html", takes_context=True)
def project_current_app(context, user, project=None):
    context.update({
        "app_object": project,
        "user": user
    })
    return context

@register.inclusion_tag("projects/nav.html", takes_context=True)
def project_nav(context, user, project=None):
    context.update({
        "nav_object": project,
        "user": user
    })
    return context

@register.tag
def list_projects(parser, token):
    """
    Example:

    {% list_projects as projects_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for project in projects %}
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

@register.inclusion_tag("projects/search-form.html", takes_context=True)
def project_search(context):
    return context
