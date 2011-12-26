from django.template import Node, Library, TemplateSyntaxError, Variable
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from base.template_tags import ListNode, parse_tag_kwargs

from courses.models import Course, CourseAttempt
from courses.utils import can_retry, get_passed_attempts

register = Library()

@register.inclusion_tag("courses/nav.html", takes_context=True)
def course_nav(context, user, course=None):
    context.update({
        "nav_object": course,
        "user": user
    })
    return context

@register.inclusion_tag("courses/search-form.html", takes_context=True)
def course_search(context):
    return context

class CourseUserStatusNode(Node):
    def __init__(self, course, user):
        self.course = Variable(course)
        self.user = Variable(user)

    def render(self, context):
        course = self.course.resolve(context)
        user = self.user.resolve(context)
        passed = get_passed_attempts(course, user)
        attempted = CourseAttempt.objects.filter(user=user, course=course).exists()
        retry, retry_time = can_retry(course, user)
        context['attempted'] = attempted
        context['has_passed'] = passed
        context['can_retry'] = retry
        context['retry_time_left'] = retry_time
        return ''
        
def course_user_status(parser, token):
    """
    Link to a user's options for a course.
    Determines if the user can retry/take a course or has already passsed.
    This will inject has_passed, retry_time_left and can_retry into the context.
    example: {% course_user_status course user %}
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, course, user = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])
    return CourseUserStatusNode(course, user)

register.tag('course_user_status', course_user_status)
