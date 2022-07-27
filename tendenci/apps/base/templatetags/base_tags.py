import re
from urllib.request import urlopen
from hashlib import md5

from tagging.templatetags.tagging_tags import TagsForObjectNode
from tagging.models import Tag
from bs4 import BeautifulStoneSoup

from django.utils.safestring import mark_safe
from django.template import Library, Node, Variable, TemplateSyntaxError
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import default_storage

from tendenci.apps.base.template_tags import parse_tag_kwargs
from tendenci.apps.base.utils import url_exists, google_cmap_sign_url
from tendenci.apps.profiles.models import Profile

from tendenci.apps.files.cache import FILE_IMAGE_PRE_KEY
from tendenci.apps.files.utils import generate_image_cache_key
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.templatetags.static import static

register = Library()

GOOGLE_SMAPS_BASE_URL = 'https://maps.googleapis.com/maps/api/staticmap'
class GoogleCMapsURL(Node):
    def __init__(self, location, origin=None, **kwargs):
        self.size = kwargs.get("size", "200x200")
        self.markers = kwargs.get("markers", 'color:red|label:A')
        self.markers_origin = kwargs.get("markers_origin", 'color:green|label:B')
        self.zoom = kwargs.get("zoom", None)
        self.location = Variable(location)
        if origin:
            self.origin_point = Variable(origin)
        else:
            self.origin_point = None

    def render(self, context):
        location = self.location.resolve(context)
        if self.origin_point:
            origin = self.origin_point.resolve(context)
        else:
            origin = None

        url = '{base_url}?center={lat}%2C{lng}&size={size}&markers={markers}%7C{lat}%2C{lng}'.format(
                                                    base_url=GOOGLE_SMAPS_BASE_URL,
                                                    lat=location.latitude,
                                                    lng=location.longitude,
                                                    size=self.size,
                                                    markers=self.markers.replace(':', '%3A').replace('|', '%7C'))
        if self.zoom:
            url = url + '&zoom=' + self.zoom

        if origin:
            url = url + '&markers={markers_origin}%7C{origin_lat}%2C{origin_lng}'.format(
                            markers_origin=self.markers_origin.replace(':', '%3A').replace('|', '%7C'),
                            origin_lat=origin['lat'],
                            origin_lng=origin['lng'])

        api_key = get_setting('module', 'locations', 'google_maps_api_key')
        if api_key:
            url = url + '&key=' + api_key

            if settings.GOOGLE_SMAPS_URL_SIGNING_SECRET:
                # sign url with signing secret
                url = google_cmap_sign_url(url)

        return url


@register.tag
def google_cmaps_url(parser, token):
    """
    Creates a url for a google static map URL.

    Examples::

        <img src="{% google_cmaps_url location size=200x200 markers=color:red|label:A zoom=8 %}" />
        <img src="{% google_cmaps_url location origin size=200x200 markers=color:red|label:A markers_origin=color:green|label:B zoom=8 %}" />
    """
    kwargs = {}
    bits = token.split_contents()
    if len(bits) < 2:
        message = "'%s' tag requires more than 1 argument" % bits[0]
        raise TemplateSyntaxError(_(message))

    location = bits[1]

    if '=' not in bits[2]:
        origin = bits[2]
    else:
        origin = None

    for bit in bits:
        if "size=" in bit:
            kwargs["size"] = bit.split("=")[1]
        if "markers=" in bit:
            kwargs["markers"] = bit.split("=")[1]
        if "markers_origin=" in bit:
            kwargs["markers_origin"] = bit.split("=")[1]
        if "zoom=" in bit:
            kwargs["zoom"] = bit.split("=")[1]

    return GoogleCMapsURL(location, origin=origin, **kwargs)

@register.inclusion_tag("base/fb_like_iframe.html")
def fb_like_button_iframe(url, show_faces='false', width=400, height=40):
    from tendenci.apps.site_settings.utils import get_setting
    site_url = get_setting('site', 'global', 'siteurl')
    url = '%s%s' % (site_url,url)
    if show_faces.lower() == 'true':
        show_faces = 'true'
    else:
        show_faces = 'false'
    try:
        width = int(width)
    except:
        width = 400
    try:
        height = int(height)
    except:
        height = 400

    return {'url': url,
            'width': width,
            'height': height,
            'show_faces':show_faces}

class FanCountNode(Node):
    def __init__(self, service, service_id):
        self.service = service
        self.service_id = service_id

    def render(self, context):
        fancount = ''
        fb_api_url = 'http://api.facebook.com/restserver.php'
        tw_api_url = 'http://api.twitter.com'

        cache_key = ''
        cache_time = 1800

        if self.service == "facebook":
            query = '%s?method=facebook.fql.query&query=SELECT%%20fan_count%%20FROM%%20page%%20WHERE%%20page_id=%s'
            xml_path = query % (fb_api_url, self.service_id)
            cache_key = md5(xml_path.encode()).hexdigest()
            fancount = cache.get(cache_key)
            if not fancount:
                try:
                    xml = urlopen(xml_path)
                    content = xml.read()
                    soup = BeautifulStoneSoup(content)
                    nodes = soup.find_all('page')
                    for node in nodes:
                        fancount = node.fan_count.string
                    cache.set(cache_key, fancount, cache_time)
                except:
                    pass

        if self.service == "twitter":
            query = "%s/1/users/show/%s.xml"
            xml_path = query % (tw_api_url, self.service_id)
            cache_key = md5(xml_path.encode()).hexdigest()
            fancount = cache.get(cache_key)
            if not fancount:
                try:
                    xml = urlopen(xml_path)
                    content = xml.read()
                    soup = BeautifulStoneSoup(content)
                    nodes = soup.find_all('user')
                    for node in nodes:
                        fancount = node.followers_count.string
                    cache.set(cache_key, fancount, cache_time)
                except:
                    pass

        return fancount

@register.tag
def fan_count(parser, token):
    """
    Pull a fan count for a social media site:

    Usage::

        {% fan_count facebook 12345 %}

        or

        {% fan_count twitter username %}

    """
    bits = token.contents.split()
    if len(bits) < 3:
        raise TemplateSyntaxError(_("'%(b)s' tag takes two arguments" % {'b':bits[0]}))
    service = bits[1]
    service_id = bits[2]
    return FanCountNode(service, service_id)

def callMethod(obj, methodName):
    """
        callMethod and args are used so that we can call a method with parameters in template
        Example:
            if you want to call: user_this.allow_view_by(user_current)
            in template: {{ user_this.profile|args:user_current|call:'allow_edit_by' }}
    """
    method = getattr(obj, methodName)

    if "__callArg" in obj.__dict__:
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()

def args(obj, arg):
    if "__callArg" not in obj.__dict__:
        obj.__callArg = []

    obj.__callArg += [arg]
    return obj

register.filter("call", callMethod)
register.filter("args", args)


# so we can create new variables in template
# {% assign [name] [value] %}
class AssignNode(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def render(self, context):
        context[self.name] = self.value.resolve(context, True)
        return ''

def do_assign(parser, token):
    """
    Assign an expression to a variable in the current context.

    Usage::
        {% assign [name] [value] %}
    Example::
        {% assign list entry.get_related %}

    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise TemplateSyntaxError(_("'%(b)s' tag takes two arguments" % {'b': bits[0]}))
    value = parser.compile_filter(bits[2])
    return AssignNode(bits[1], value)

register.tag('assign', do_assign)


class GetProfileNode(Node):
    def __init__(self, obj, var_name):
        self.user_obj = obj
        self.var_name = var_name

    def resolve(self, var, context):
        """Resolves a variable out of context if it's not in quotes"""
        if var[0] in ('"', "'") and var[-1] == var[0]:
            return var[1:-1]
        else:
            return Variable(var).resolve(context)

    def render(self, context):
        user_obj = self.resolve(self.user_obj, context)
        var_name = self.resolve(self.var_name, context)
        if isinstance(user_obj, User):
            try:
                profile = user_obj.profile
            except Profile.DoesNotExist:
                profile = Profile.objects.create_profile(user=user_obj)
            context[var_name] = profile
        return ""

def get_or_create_profile_for(parser, token):
    """
    Get or create a user profile if not exists

    Example::
        {% get_or_create_profile user_this %}

    """
    bits = token.contents.split()
    if len(bits) < 2:
        raise TemplateSyntaxError(_("'%(b)s' tag takes at least two arguments" % {'b':bits[0]}))

    args = {
        'obj': bits[1],
        'var_name': next_bit_for(bits, 'as'),
    }
    return GetProfileNode(**args)

def next_bit_for(bits, key, if_none=None, step=1):
    try:
        return bits[bits.index(key)+step]
    except ValueError:
        return if_none

register.tag('get_or_create_profile_for', get_or_create_profile_for)

class ResetNode(Node):
    def __init__(self, variable, **kwargs):
        # set the context var
        self.variable = Variable(variable)

        # get the context vars
        for k, v in kwargs.items():
            if k == 'context':
                self.context = v

    def render(self, context):
        variable = self.variable.resolve(context)
        context[self.context] = variable
        return ''

@register.tag
def reset(parser, token):
    """
    Reset a context variable to another one

    Usage::
        {% reset var as var1 %}
    """
    bits = token.split_contents()

    try:
        variable = bits[1]
    except:
        raise TemplateSyntaxError(_("'%(b)s' requires at least three arguments." % {'b':bits[0]}))

    if bits[1] == 'as':
        raise TemplateSyntaxError(_("'%(b)s' first argument must be a context var." % {'b':bits[0]}))

    # get the user
    try:
        variable = bits[bits.index('as')-1]
        context = bits[bits.index('as')+1]
    except:
        variable = None
        context = None

    if not variable and not context:
        raise TemplateSyntaxError(_("'%(b)s' missing arguments. Syntax {% reset var1 as var2 %}" % {'b':bits[0]}))

    return ResetNode(variable, context=context)

class ImagePreviewNode(Node):
    def __init__(self, instance, size, **kwargs):
        # set the context var
        self.instance = Variable(instance)
        self.size = size
        self.context = None

        # get the context vars
        for k, v in kwargs.items():
            if k == 'context':
                self.context = v

    def render(self, context):
        instance = self.instance.resolve(context)

        app_label = instance._meta.app_label
        model = instance._meta.object_name.lower()

        url = reverse('image_preview', args=(app_label, model, instance.id, self.size))
        if not url_exists(url):
            url = None

        if self.context:
            context[self.context] = url
        else:
            context['image_preview'] = url

        return ''

@register.tag
def image_preview(parser, token):
    """
        Gets the url for an image preview base
        on model and model_id
    """
    bits = token.split_contents()

    try:
        instance = bits[1]
    except:
        raise TemplateSyntaxError(_("'%(b)s' requires at least 2 arguments" % {'b':bits[0]}))

    try:
        size = bits[2]
    except:
        raise TemplateSyntaxError(_("'%(b)s' requires at least 2 arguments" % {'b':bits[0]}))

    try:
        context = bits[4]
    except:
        context = "image_preview"

    return ImagePreviewNode(instance, size, context=context)


class RssParserNode(Node):
    def __init__(self, context_var, url, *args, **kwargs):
        self.url = url
        self.context_var = context_var
        self.kwargs = kwargs

    def render(self, context):
        import feedparser

        cache_timeout = 300

        if 'cache' in self.kwargs:
            try:
                cache_timeout = Variable(self.kwargs['cache'])
                cache_timeout = cache_timeout.resolve(context)
            except:
                cache_timeout = self.kwargs['cache']

        try:
            url = Variable(self.url)
            url = url.resolve(context)
            self.url = url
        except:
            pass

        cache_key = md5(self.url.encode()).hexdigest()
        url_content = cache.get(cache_key)

        if url_content is None:
            url_content = feedparser.parse(self.url)
            # We are going to try to pop out the errors in the
            # feed because they raise an exception that can't be
            # pickled when we try to cache the content.
            if 'bozo_exception' in url_content:
                url_content['bozo_exception'] = ''
            cache.set(cache_key, url_content, int(cache_timeout))

        context[self.context_var] = url_content

        return ''


@register.tag(name="get_rss")
def get_rss(parser, token):
    """
    Take an RSS feed so you can iterate through the entries.

    Usage::

        {% get_rss [rss_feed_url] as [variable] cache=600 %}

    Options include:

        ``cache``
           The length of time to cache the feed in seconds. **Default: 300**

    Example 1::

        {% get_rss "http://www.freesound.org/blog/?feed=rss2" as rss %}
        {% for entry in rss.entries %}
            <h1>{{entry.title}}</h1>
            <p>
                {{entry.summary|safe}}
            </p>
            <p>
                <a href="{{entry.link}}">read more...</a>
            </p>
        {% endfor %}


    Example 2::

        {% get_rss "http://rss.nytimes.com/services/xml/rss/nyt/PersonalTech.xml" as rss %}
        {% if rss.feed.image %}
            <img src="{{ rss.feed.image.href }}" alt="" />
        {% endif %}
        {% for entry in rss.entries %}
        <div class="row entry-item">

             <div class="col-xs-4 col-md-3">
             {# media image #}
              {% if entry.media_content %}
                  {% for media in entry.media_content %}
                      {% if media.medium == 'image' %}
                      <img src="{{ media.url }}" width="{{ media.width }}" height="{{ media.height }}" alt="" />
                      {% endif %}
                  {% endfor %}
              {% endif %}
               </div>

              <div class="col-xs-8 col-md-9">
                  {# title #}
                  <h4 class="entry-title"><a href="{{ entry.link }}">{{entry.title}}</a></h4>

                  {# pubdate #}
                  <div class="small">Published on: {{entry.published}}</div>

                  {# authors #}
                  {% if entry.authors %}
                      <div class="small">Author{{ entry.authors|pluralize }}:
                      {% for author in entry.authors %}
                          {{ author.name }}
                    {% endfor %}
                      </div>
                {% endif %}

                {# categories #}
                {% if entry.tags %}
                      <div class="small">Categories:
                      {% for tag in entry.tags %}
                          {% if tag.scheme  %}
                          <a href="{{ tag.scheme }}">{{ tag.term }}</a>
                          {% else  %}
                          {{ tag.term }}
                          {% endif %}
                    {% endfor %}
                      </div>
                {% endif %}

                {# description #}
                {% if entry.content %}
                  {% for content in entry.content %}
                      <div>{{ content.value|safe }}</div>
                  {% endfor %}
                {% elif entry.summary %}
                  <div>{{ entry.summary|safe }}</div>
                {% endif %}

                {# enclosure #}
                {% if entry.links %}
                  {% for link in entry.links %}
                      {% if link.rel == 'enclosure' %}
                      <div>
                       <audio controls>
                          <source src="{{ link.href }}" type="{{ link.type }}">
                        </audio>
                        {{ link.length|filesizeformat }}
                        </div>
                      {% endif %}
                  {% endfor %}
                {% endif %}

              <a href="{{entry.link}}">read more...</a>
           </div>

        </div>
        {% endfor %}



    """
    args, kwargs = [], {}
    bits = token.split_contents()
    url_string = bits[1]
    context_var = bits[3]

    if len(bits) < 4:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[2] != "as":
        message = "'%s' third argument must be 'as" % bits[0]
        raise TemplateSyntaxError(_(message))

    kwargs = parse_tag_kwargs(bits)

    if url_string[0] == url_string[-1] and url_string[0] in ('"', "'"):
        url = url_string[1:-1]
    else:
        url = url_string

    return RssParserNode(context_var, url, *args, **kwargs)


class Md5Hash(Node):

    def __init__(self, *args, **kwargs):
        self.bits = [Variable(bit) for bit in kwargs.get("bits", [])[1:]]

    def render(self, context):
        bits = [str(b.resolve(context)) for b in self.bits]
        return md5(".".join(bits).encode()).hexdigest()

@register.tag
def md5_hash(parser, token):
    """
    Example::
        {% md5_hash obj.pk obj.email %}
    """
    args, kwargs = [], {}
    kwargs["bits"] = token.split_contents()

    if len(kwargs["bits"]) < 2:
        message = "'%s' tag requires more than 2" % kwargs["bits"][0]
        raise TemplateSyntaxError(_(message))

    return Md5Hash(*args, **kwargs)

class NoWhiteSpaceNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        text = self.nodelist.render(context).strip()
        return re.sub(r'\s{2,}', ' ', text)

@register.tag
def nowhitespace(parser, token):
    """
    Replaces two or more spaces between regular text
    (*NOT* HTML) down to on space
    """
    nodelist = parser.parse(('endnowhitespace',))
    parser.delete_first_token()
    return NoWhiteSpaceNode(nodelist)


class PhotoImageURL(Node):
    def __init__(self, photo, *args, **kwargs):
        self.size = kwargs.get("size", "100x100")
        self.crop = kwargs.get("crop", False)
        self.constrain = kwargs.get("constrain", False)
        self.quality = kwargs.get("quality", 90)
        self.photo = Variable(photo)

    def render(self, context):
        photo = self.photo.resolve(context)

        # We can't crop and constrain, so we need
        # to pick one if both are passed
        if self.crop and self.constrain:
            self.constrain = False

        # return empty unicode string
        if not photo.pk:
            return static(settings.DEFAULT_IMAGE_URL)

        cache_key = generate_image_cache_key(file=str(photo.pk), size=self.size, pre_key="photo", crop=self.crop, unique_key=str(photo.pk), quality=self.quality, constrain=self.constrain)
        cached_image_url = cache.get(cache_key)
        if cached_image_url:
            if settings.USE_S3_STORAGE:
                return default_storage.url(cached_image_url)
            return cached_image_url

        args = [photo.pk, self.size]
        if self.crop:
            args.append("crop")
        if self.constrain:
            args.append("constrain")
        if self.quality:
            args.append(self.quality)
        url = reverse('photo.size', args=args)
        return url


@register.tag
def photo_image_url(parser, token):
    """
    Creates a url for a photo that can be resized, cropped, and have quality reduced.
    Used specifically for photos.

    Example::

        {% list_photos as photos user=user limit=3 %}
        {% for photo in photos %}
            <img src="{% photo_image_url photo size=100x100 crop=True constrain=True %}" />
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    photo = bits[1]

    for bit in bits:
        if "size=" in bit:
            kwargs["size"] = bit.split("=")[1]
        if "crop=" in bit:
            kwargs["crop"] = bool(bit.split("=")[1])
        if "constrain=" in bit:
            kwargs["constrain"] = bool(bit.split("=")[1])
        if "quality=" in bit:
            kwargs["quality"] = bit.split("=")[1]

    if len(bits) < 1:
        message = "'%s' tag requires more than 1 argument" % bits[0]
        raise TemplateSyntaxError(_(message))

    return PhotoImageURL(photo, *args, **kwargs)


class ImageURL(Node):
    def __init__(self, file, *args, **kwargs):
        self.size = kwargs.get("size", None)
        self.crop = kwargs.get("crop", False)
        self.quality = kwargs.get("quality", None)
        self.constrain = kwargs.get("constrain", None)
        self.file = Variable(file)

    def render(self, context):
        file = self.file.resolve(context)

        if file and file.pk:

            cache_key = generate_image_cache_key(file=str(file.id), size=self.size, pre_key=FILE_IMAGE_PRE_KEY, crop=self.crop, unique_key=str(file.id), quality=self.quality, constrain=self.constrain)
            cached_image_url = cache.get(cache_key)
            if cached_image_url:
                if settings.USE_S3_STORAGE:
                    return default_storage.url(cached_image_url)
                return cached_image_url

            args = [file.pk]
            if self.size:
                try:
                    size = Variable(self.size)
                    size = size.resolve(context)
                except:
                    size = self.size
                args.append(size)
            if self.crop:
                args.append("crop")
            if self.constrain:
                args.append("constrain")
            if self.quality:
                args.append(self.quality)
            url = reverse('file', args=args)
            return url

        # return the default image url
        return static(settings.DEFAULT_IMAGE_URL)


@register.tag
def image_url(parser, token):
    """
    Creates a url for a photo that can be resized, cropped, constrianed, and have quality reduced.

    Usage::

        {% image_url file [options][size=100x100] [crop=True] [constrain=True] [quality=90] %}

    Options include:

        ``size``
           The size in the format [width]x[height]. **Default: 100x100**
        ``crop``
           Whether or not to crop the image. **Default: False**
        ``quality``
           The quality of the rendered image. Use smaller for faster loading. Must be used with ``size`` **Default: 90**
        ``constrain``
            The size of the image will be constrained instead of cropped

    Example::

        <img src="{% image_url file size=150x100 crop=True quality=90 %}" />
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    file = bits[1]

    for bit in bits:
        if "size=" in bit:
            kwargs["size"] = bit.split("=")[1]
        if "crop=" in bit:
            kwargs["crop"] = bool(bit.split("=")[1])
        if "constrain=" in bit:
            kwargs["constrain"] = bool(bit.split("=")[1])
        if "quality=" in bit:
            kwargs["quality"] = bit.split("=")[1]

    if len(bits) < 1:
        message = "'%s' tag requires more than 1 argument" % bits[0]
        raise TemplateSyntaxError(_(message))

    return ImageURL(file, *args, **kwargs)

class NonHashedTagsNode(TagsForObjectNode):
    def render(self, context):
        context[self.context_var] = \
            Tag.objects.get_for_object(self.obj.resolve(context)).exclude(
            name__contains='#')
        return ''

class HashedTagsNode(TagsForObjectNode):
    def render(self, context):
        context[self.context_var] = \
            Tag.objects.get_for_object(self.obj.resolve(context)).filter(
            name__contains='#')
        return ''

def do_non_hash_tags_for_object(parser, token):
    """
    Retrieves a list of ``Tag`` objects that DO NOT start with '#'
    associated with an object and stores them in a context variable.

    Usage::

       {% tags_strip_hash [object] as [varname] %}

    Example::

        {% tags_strip_hash foo_object as tag_list %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError(_('%s tag requires exactly three arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    return NonHashedTagsNode(bits[1], bits[3])

def do_hash_tags_for_object(parser, token):
    """
    Retrieves a list of ``Tag`` objects that START with '#'
    associated with an object and stores them in a context variable.

    Usage::

       {% tags_hash_tags[object] as [varname] %}

    Example::

        {% tags_hash_tags foo_object as tag_list %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError(_('%s tag requires exactly three arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    return HashedTagsNode(bits[1], bits[3])

register.tag('tags_strip_hash', do_non_hash_tags_for_object)
register.tag('tags_hash_tags', do_hash_tags_for_object)

@register.inclusion_tag("base/meta_creator_owner.html")
def meta_creator_owner(obj):
    return {'obj': obj}

@register.inclusion_tag("base/stock_image_url.html", takes_context=True)
def stock_image_url(context, size):
    context.update({'size': size})
    return context


@register.simple_tag
def all_tags_list():
    """
    Creates a text list of tags for use in a dropdown
    """
    tags = Tag.objects.all()
    tag_list = ",".join(['"%s"' % t.name for t in tags])
    return mark_safe(tag_list)
