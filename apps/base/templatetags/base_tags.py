import re
import urllib2
from hashlib import md5

from BeautifulSoup import BeautifulStoneSoup
from django.template import Library, Node, Variable, TemplateSyntaxError
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.cache import cache

from base.utils import url_exists
from profiles.models import Profile
from tagging.templatetags.tagging_tags import TagsForObjectNode
from tagging.models import Tag

register = Library()


@register.inclusion_tag("base/fb_like_iframe.html")
def fb_like_button_iframe(url, show_faces='false', width=400, height=30):
    from site_settings.utils import get_setting
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
            cache_key = md5(xml_path).hexdigest()
            fancount = cache.get(cache_key)
            if not fancount:
                try:
                    xml = urllib2.urlopen(xml_path)
                    content = xml.read()
                    soup = BeautifulStoneSoup(content)
                    nodes = soup.findAll('page')
                    for node in nodes:
                        fancount = node.fan_count.string
                    cache.set(cache_key, fancount, cache_time)
                except:
                    pass

        if self.service == "twitter":
            query = "%s/1/users/show/%s.xml"
            xml_path = query % (tw_api_url, self.service_id)
            cache_key = md5(xml_path).hexdigest()
            fancount = cache.get(cache_key)
            if not fancount:
                try:
                    xml = urllib2.urlopen(xml_path)
                    content = xml.read()
                    soup = BeautifulStoneSoup(content)
                    nodes = soup.findAll('user')
                    for node in nodes:
                        fancount = node.followers_count.string
                    cache.set(cache_key, fancount, cache_time)
                except:
                    pass

        return fancount
    
@register.tag
def fan_count(parser, token):
    """
        {% fan_count facebook 12345 %}
        or
        {% fan_count twitter username %}
    """
    bits = token.contents.split()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' tag takes two arguments" % bits[0])
    service = bits[1]
    service_id = bits[2]
    return FanCountNode(service, service_id)

def callMethod(obj, methodName):
    """
        callMethod and args are used so that we can call a method with parameters in template
        Example:
            if you want to call: user_this.allow_view_by(user_current)
            in template: {{ user_this.get_profile|args:user_current|call:'allow_edit_by' }}
    """
    method = getattr(obj, methodName)
 
    if obj.__dict__.has_key("__callArg"):
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()
 
def args(obj, arg):
    if not obj.__dict__.has_key("__callArg"):
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
    
    Syntax::
        {% assign [name] [value] %}
    Example::
        {% assign list entry.get_related %}
        
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise TemplateSyntaxError("'%s' tag takes two arguments" % bits[0])
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
                profile = user_obj.get_profile()
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
        raise TemplateSyntaxError("'%s' tag takes at least two arguments" % bits[0])
    
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
        {% reset var as var1 %} 
    """
    bits = token.split_contents()

    try:
        variable = bits[1]
    except:
        raise TemplateSyntaxError, "'%s' requires at least three arguments." % bits[0]
    
    if bits[1] == 'as':
        raise TemplateSyntaxError, "'%s' first argument must be a context var." % bits[0]
    
    # get the user
    try:
        variable = bits[bits.index('as')-1]
        context = bits[bits.index('as')+1]
    except:
        variable = None
        context = None
    
    if not variable and not context:
        raise TemplateSyntaxError, "'%s' missing arguments. Syntax {% reset var1 as var2 %}" % bits[0]
    
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
        raise TemplateSyntaxError, "'%s' requires at least 2 arguments" % bits[0]
        
    try:
        size = bits[2]
    except:
        raise TemplateSyntaxError, "'%s' requires at least 2 arguments" % bits[0]        
         
    try:
        context = bits[4]
    except:
        context = "image_preview"
        
    return ImagePreviewNode(instance, size, context=context)

class RssParserNode(Node):
    def __init__(self, var_name, url=None, url_var_name=None):
        self.url = url
        self.url_var_name = url_var_name
        self.var_name = var_name

    def render(self, context):
        import feedparser
        if self.url:
            context[self.var_name] = feedparser.parse(self.url)
        else:
            try:
                context[self.var_name] = feedparser.parse(context[self.url_var_name])
            except KeyError:
                raise TemplateSyntaxError, "the variable \"%s\" can't be found in the context" % self.url_var_name
        return ''

@register.tag(name="get_rss")
def get_rss(parser, token):
    """
    example usage:
    
    {% load cache %}
    {% load rss %}
    
    {% cache 500 rss_display %}
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
    {% endcache %}
    """
    import re
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    url, var_name = m.groups()
    
    if url[0] == url[-1] and url[0] in ('"', "'"):
        return RssParserNode(var_name, url=url[1:-1])
    else:
        return RssParserNode(var_name, url_var_name=url)

class Md5Hash(Node):
    
    def __init__(self, *args, **kwargs):
        self.bits = [Variable(bit) for bit in kwargs.get("bits", [])[1:]]

    def render(self, context):
        from hashlib import md5
        bits = [str(b.resolve(context)) for b in self.bits]
        return md5(".".join(bits)).hexdigest()

@register.tag
def md5_hash(parser, token):
    """
    Example:
        {% md5_hash obj.pk obj.email %}
    """
    args, kwargs = [], {}
    kwargs["bits"] = token.split_contents()

    if len(kwargs["bits"]) < 2:
        message = "'%s' tag requires more than 2" % kwargs["bits"][0]
        raise TemplateSyntaxError(message)

    return Md5Hash(*args, **kwargs)

class NoWhiteSpaceNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        text = self.nodelist.render(context).strip()
        return re.sub('\s{2,}', ' ', text)

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
        self.quality = kwargs.get("quality", 90)
        self.photo = Variable(photo)

    def render(self, context):
        photo = self.photo.resolve(context)

        # return empty unicode string
        if not photo.pk:
            return unicode('')

        args = [photo.pk, self.size]
        if self.crop:
            args.append("crop")
        if self.quality:
            args.append(self.quality)
        url = reverse('photo.size', args=args)
        return url


@register.tag
def photo_image_url(parser, token):
    """
    Example:
        {% list_photos as photos user=user limit=3 %}
        {% for photo in photos %}
            <img src="{% photo_image_url photo size=100x100 crop=True %}" />
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
        if "quality=" in bit:
            kwargs["quality"] = bit.split("=")[1]

    if len(bits) < 1:
        message = "'%s' tag requires more than 1 argument" % bits[0]
        raise TemplateSyntaxError(message)

    return PhotoImageURL(photo, *args, **kwargs)


class ImageURL(Node):
    def __init__(self, file, *args, **kwargs):
        self.size = kwargs.get("size", "100x100")
        self.crop = kwargs.get("crop", False)
        self.quality = kwargs.get("quality", 90)
        self.file = Variable(file)

    def render(self, context):
        file = self.file.resolve(context)

        # return empty unicode string
        if not file.pk:
            return unicode('')

        args = [file.pk, self.size]
        if self.crop:
            args.append("crop")
        if self.quality:
            args.append(self.quality)
        url = reverse('file', args=args)
        return url

  
@register.tag
def image_url(parser, token):
    """
    Example:
        <img src="{% image_url file size=100x100 crop=True quality=90 %}" />
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    file = bits[1]

    for bit in bits:
        if "size=" in bit:
            kwargs["size"] = bit.split("=")[1]
        if "crop=" in bit:
            kwargs["crop"] = bool(bit.split("=")[1])
        if "quality=" in bit:
            kwargs["quality"] = bit.split("=")[1]

    if len(bits) < 1:
        message = "'%s' tag requires more than 1 argument" % bits[0]
        raise TemplateSyntaxError(message)

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
