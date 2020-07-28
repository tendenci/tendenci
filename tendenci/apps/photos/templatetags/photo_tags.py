from builtins import str
import re

from django.template import Node, Library, TemplateSyntaxError, Variable, VariableDoesNotExist
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.photos.models import Image, Pool, PhotoSet
from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs


register = Library()


class PrintExifNode(Node):
    def __init__(self, exif):
        self.exif = exif

    def render(self, context):
        try:
            exif = str(self.exif.resolve(context, True))
        except VariableDoesNotExist:
            exif = u''

        EXPR = r"'(?P<key>[^:]*)':(?P<value>[^,]*),"
        expr = re.compile(EXPR)
        msg = "<table>"
        for i in expr.findall(exif):
            msg += "<tr><td>%s</td><td>%s</td></tr>" % (i[0], i[1])

        msg += "</table>"

        return u'<div id="exif">%s</div>' % (msg)


@register.tag(name="print_exif")
def do_print_exif(parser, token):
    try:
        tag_name, exif = token.contents.split()
    except ValueError:
        msg = '%r tag requires a single argument' % token.contents[0]
        raise TemplateSyntaxError(_(msg))

    exif = parser.compile_filter(exif)
    return PrintExifNode(exif)


class PublicPhotosNode(Node):
    def __init__(self, context_var, user_var=None, use_pool=False):
        self.context_var = context_var
        if user_var is not None:
            self.user_var = Variable(user_var)
        else:
            self.user_var = None
        self.use_pool = use_pool

    def render(self, context):
        use_pool = self.use_pool

        if use_pool:
            queryset = Pool.objects.filter(
                photo__is_public=True,
            ).select_related("photo")
        else:
            queryset = Image.objects.filter(is_public=True).order_by('-date_added')

        if self.user_var is not None:
            user = self.user_var.resolve(context)
            if use_pool:
                queryset = queryset.filter(photo__member=user)
            else:
                queryset = queryset.filter(member=user)

        context[self.context_var] = queryset
        return ""


@register.tag
def public_photos(parser, token, use_pool=False):

    bits = token.split_contents()

    if len(bits) != 3 and len(bits) != 5:
        message = "'%s' tag requires three or five arguments" % bits[0]
        raise TemplateSyntaxError(_(message))
    else:
        if len(bits) == 3:
            if bits[1] != 'as':
                message = "'%s' second argument must be 'as'" % bits[0]
                raise TemplateSyntaxError(_(message))

            return PublicPhotosNode(bits[2], use_pool=use_pool)

        elif len(bits) == 5:
            if bits[1] != 'for':
                message = "'%s' second argument must be 'for'" % bits[0]
                raise TemplateSyntaxError(message)
            if bits[3] != 'as':
                message = "'%s' forth argument must be 'as'" % bits[0]
                raise TemplateSyntaxError(_(message))

            return PublicPhotosNode(bits[4], bits[2], use_pool=use_pool)


@register.tag
def public_pool_photos(parser, token):
    return public_photos(parser, token, use_pool=True)


@register.inclusion_tag("photos/options.html", takes_context=True)
def photo_options(context, user, photo):
    context.update({
        "opt_object": photo,
        "user": user
    })
    return context


@register.inclusion_tag("photos/nav.html", takes_context=True)
def photo_nav(context, user, photo=None):
    context.update({
        "nav_object": photo,
        "user": user
    })
    return context

@register.inclusion_tag("photos/search-form.html", takes_context=True)
def photo_search(context):
    return context


@register.inclusion_tag("photos/top_nav_items.html", takes_context=True)
def photo_current_app(context, user, photo=None):
    context.update({
        "app_object": photo,
        "user": user
    })
    return context

@register.inclusion_tag("photos/photo-set/top_nav_items.html", takes_context=True)
def photo_set_current_app(context, user, photo_set=None):
    context.update({
        "app_object": photo_set,
        "user": user
    })
    return context

@register.inclusion_tag("photos/photo-set/options.html", takes_context=True)
def photo_set_options(context, user, photo_set):
    context.update({
        "opt_object": photo_set,
        "user": user
    })
    return context


@register.inclusion_tag("photos/photo-set/nav.html", takes_context=True)
def photo_set_nav(context, user, photo_set=None):
    context.update({
        "nav_object": photo_set,
        "user": user
    })
    return context


@register.inclusion_tag("photos/photo-set/search-form.html", takes_context=True)
def photo_set_search(context):
    return context


class ListPhotosNode(ListNode):
    model = Image
    perms = 'photos.view_image'


@register.tag
def list_photos(parser, token):
    """
    Used to pull a list of :model:`photos.Image` items.

    Usage::

        {% list_photos as [varname] [options] %}

    Be sure the [varname] has a specific name like ``photos_sidebar`` or
    ``photos_list``. Options can be used as [option]=[value]. Wrap text values
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

        {% list_photos as photos_list limit=5 tags="cool" %}
        {% for photo in photos_list %}
            {{ photo.title }}
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

    return ListPhotosNode(context_var, *args, **kwargs)


class ListPhotoSetsNode(ListNode):
    model = PhotoSet
    perms = 'photos.view_photoset'


@register.tag
def list_photo_sets(parser, token):
    """
    Used to pull a list of :model:`photos.PhotoSet` items.

    Usage::

        {% list_photo_sets as [varname] [options] %}

    Be sure the [varname] has a specific name like ``photo_sets_sidebar`` or
    ``photo_sets_list``. Options can be used as [option]=[value]. Wrap text
    values in quotes like ``tags="cool"``. Options include:

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

        {% list_photo_sets as photo_sets_list limit=5 tags="cool" %}
        {% for photo_set in photo_sets_list %}
            {{ photo_set.name }}
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

    return ListPhotoSetsNode(context_var, *args, **kwargs)
