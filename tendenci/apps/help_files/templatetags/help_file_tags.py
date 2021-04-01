from django.template import Library, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.apps.help_files.models import HelpFile


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


@register.inclusion_tag("help_files/top_nav_items.html", takes_context=True)
def help_file_current_app(context, user, help_file=None):
    context.update({
        "app_object": help_file,
        "user": user
    })
    return context


@register.inclusion_tag("help_files/search-form.html", takes_context=True)
def help_file_search(context):
    return context


class ListHelpFilesNode(ListNode):
    model = HelpFile
    perms = 'help_files.view_helpfile'


@register.tag
def list_helpfiles(parser, token):
    """
    Used to pull a list of :model:`help_files.HelpFile` items.

    Usage::

        {% list_help_files as [varname] [options] %}

    Be sure the [varname] has a specific name like ``help_files_sidebar`` or
    ``help_files_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:

        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Latest Created**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.
        ``filters``
            Use only single quotes for text where needed. These will be placed inside Q() tags. 
            Use &, |, and commas to separate values. 
            Only one operator is allowed per comma separated group.
            Each comma separated group will be applied in a single statement.
            If more is required a custom function should be made.
            ex: {% list_helpfiles as help_files_list filters="is_faq=True&is_featured=True" %}

    Example::

        {% list_helpfiles as help_files_list limit=5 tags="cool" %}
        {% for help_file in help_files_list %}
            {{ help_file.question }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[1] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(_(message))

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListHelpFilesNode(context_var, *args, **kwargs)
