from django.template import Node, Library, TemplateSyntaxError, Variable

from courses.models import Course
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListCoursesNode(ListNode):
    model = Course


@register.tag
def list_courses(parser, token):
    """
    Example:

    {% list_courses as courses_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for course in courses %}
        {{ course.something }}
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

    return ListCoursesNode(context_var, *args, **kwargs)
