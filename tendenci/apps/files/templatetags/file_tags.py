from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist
from django.utils.translation import ugettext_lazy as _
from tendenci.apps.files.models import File
from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs

register = Library()


@register.inclusion_tag("files/options.html", takes_context=True)
def file_options(context, user, file):
    context.update({
        "opt_object": file,
        "user": user
    })
    return context


@register.inclusion_tag("files/nav.html", takes_context=True)
def file_nav(context, user, file=None):
    context.update({
        "nav_object": file,
        "user": user
    })
    return context


@register.inclusion_tag("files/search-form.html", takes_context=True)
def file_search(context):
    return context


@register.inclusion_tag("files/top_nav_items.html", takes_context=True)
def file_current_app(context, user, file=None):
    context.update({
        "app_object": file,
        "user": user
    })
    return context


@register.inclusion_tag("files/thumbnail.html", takes_context=True)
def file_thumbnail(context, layout, file_obj):
    use_image = False
    if layout == 'grid' and file_obj.type() == 'image':
        use_image = True

    context.update({
        "use_image": use_image,
    })
    return context


@register.inclusion_tag('files/reports/most-viewed-result.html', takes_context=True)
def most_viewed_result(context):
    event_log = context['event_log']
    [context['file']] = File.objects.filter(pk=event_log['object_id'])[:1] or [None]
    return context


class FilesForModelNode(Node):

    def __init__(self, context_var, *args, **kwargs):
        self.kwargs = kwargs
        self.context_var = context_var

    def render(self, context):
        instance = self.kwargs['instance']

        try:
            instance = Variable(instance).resolve(context)
        except VariableDoesNotExist:
            return ''

        files = File.objects.get_for_model(instance)

        context[self.context_var] = files
        return ''


@register.tag
def files_for_model(parser, token):
    """
    Pull a list of :model:`File` objects based on another model.

    Example::

        {% files_for_model speaker as speaker_files %}
        {% for file in speaker_files %}
            {{ file.file }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[3]
    kwargs['instance'] = bits[1]

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[2] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(_(message))

    return FilesForModelNode(context_var, *args, **kwargs)


@register.filter
def size(file, size):
    """
    size examples:
        size = '100x200'
        size = '100'
        size = '100x'
        size = 'x100'
        size = '100x200/constrain'
    """
    from django.core.urlresolvers import reverse

    if not isinstance(file, File):
        return u''

    options = u''

    if '/' in size:
        size, options = size.split('/')

    kwargs = {
        'id': unicode(file.pk),
        'size': size,
    }

    if 'constrain' in options:
        kwargs['constrain'] = 'constrain'

    return reverse('file', kwargs=kwargs)


class ListFilesNode(ListNode):
    model = File
    perms = 'files.view_file'


@register.tag
def list_files(parser, token):
    """
    Used to pull a list of :model:`files.File` items.

    Usage::

        {% list_files as [varname] [options] %}

    Be sure the [varname] has a specific name like ``files_sidebar`` or
    ``files_list``. Options can be used as [option]=[value]. Wrap text values
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
        ``group``
           The group id associated with items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_files as files_list limit=5 tags="cool" %}
        {% for file in files_list %}
            {{ file.name }}
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

    return ListFilesNode(context_var, *args, **kwargs)
