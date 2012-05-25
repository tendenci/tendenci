from django.template import Node, Library, TemplateSyntaxError, Variable
from django.contrib.auth.models import AnonymousUser

from architecture_projects.models import ArchitectureProject
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


@register.inclusion_tag("architecture_projects/options.html", takes_context=True)
def architecture_project_options(context, user, architecture_project):
    context.update({
        "opt_object": architecture_project,
        "user": user
    })
    return context


@register.inclusion_tag("architecture_projects/search-form.html", takes_context=True)
def architecture_project_search(context):
    return context


class ListArchitectureProjectNode(ListNode):
    model = ArchitectureProject


@register.tag
def list_architecture_projects(parser, token):
    """
    Used to pull a list of :model:`architecture_projects.ArchitectureProject` items.

    Usage::

        {% list_architecture_projects as [varname] [options] %}

    Be sure the [varname] has a specific name like ``architecture_projects_sidebar`` or 
    ``architecture_projects_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:
    
        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Newest Added**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_architecture_projects as architecture_projects_list limit=5 tags="cool" %}
        {% for cs in architecture_projects_list %}
            {{ cs.client }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires at least 2 parameters" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListArchitectureProjectNode(context_var, *args, **kwargs)
