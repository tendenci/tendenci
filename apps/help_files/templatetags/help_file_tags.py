from django.template import Library, TemplateSyntaxError
from base.template_tags import ListNode, parse_tag_kwargs
from help_files.models import HelpFile

register = Library()

@register.inclusion_tag("help_files/options.html", takes_context=True)
def help_file_options(context, user, help_file):
    context.update({
        "opt_object": help_file,
        "user": user
    })
    return context

@register.inclusion_tag("help_files/nav.html", takes_context=True)
def help_file_nav(context, user, help_file=None):
    context.update({
        "nav_object" : help_file,
        "user": user
    })
    return context

@register.inclusion_tag("help_files/search-form.html", takes_context=True)
def help_file_search(context):
    return context

class ListHelpFilesNode(ListNode):
    model = HelpFile


@register.tag
def list_helpfiles(parser, token):
    """
    Example:
        {% list_helpfiles as help_files [user=user limit=3 tags=bloop bleep] %}
        {% for help_file in help_files %}
            <p>{{ help_file.question }}</p>
        {% endfor %}

    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-release_dt'

    return ListHelpFilesNode(context_var, *args, **kwargs)