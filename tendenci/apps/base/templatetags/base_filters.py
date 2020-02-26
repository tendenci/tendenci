from builtins import str
import re
import os
import pytz
import codecs
from PIL import Image
from dateutil.parser import parse
from datetime import datetime

from decimal import Decimal
from django.template import Library
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape, strip_tags, urlize
from django.contrib.auth.models import AnonymousUser
from django.core.files.storage import default_storage

from tendenci.apps.base.utils import strip_entities, strip_html

register = Library()


@register.filter(name="localize_date")
def localize_date(value, to_tz=None):
    from tendenci.apps.base.utils import adjust_datetime_to_timezone
    try:
        if to_tz is None:
            to_tz = settings.UI_TIME_ZONE

        from_tz = settings.TIME_ZONE

        return adjust_datetime_to_timezone(value, from_tz=from_tz, to_tz=to_tz)
    except AttributeError:
        return ''
localize_date.is_safe = True

@register.filter_function
def date_short(value, arg=None):
    """Formats a date according to the given format."""
    from django.utils.dateformat import format
    from tendenci.apps.site_settings.utils import get_setting
    if not value:
        return u''
    if arg is None:
        s_date_format = get_setting('site', 'global', 'dateformat')
        if s_date_format:
            arg = s_date_format
        else:
            arg = settings.SHORT_DATETIME_FORMAT
    try:
        return formats.date_format(value, arg)
    except AttributeError:
        try:
            return format(value, arg)
        except AttributeError:
            return ''
date_short.is_safe = False

@register.filter_function
def date_long(value, arg=None):
    """Formats a date according to the given format."""
    from django.utils.dateformat import format
    from tendenci.apps.site_settings.utils import get_setting
    if not value:
        return u''
    if arg is None:
        s_date_format = get_setting('site', 'global', 'dateformatlong')
        if s_date_format:
            arg = s_date_format
        else:
            arg = settings.DATETIME_FORMAT
    try:
        return formats.date_format(value, arg)
    except AttributeError:
        try:
            return format(value, arg)
        except AttributeError:
            return ''
date_long.is_safe = False

@register.filter_function
def date(value, arg=None):
    """Formats a date according to the given format."""
    from django.utils.dateformat import format
    if not value:
        return u''
    if arg is None:
        arg = settings.DATETIME_FORMAT
    else:
        if arg == 'long':
            return date_long(value)
        if arg == 'short':
            return date_short(value)
    try:
        return formats.date_format(value, arg)
    except AttributeError:
        try:
            return format(value, arg)
        except AttributeError:
            return ''
date_long.is_safe = False

@register.filter_function
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)

@register.filter_function
def str_to_date(string, args=None):
    """Takes a string and converts it to a datetime object"""
    date = parse(string)
    if date:
        return date
    return ''

@register.filter_function
def exif_to_date(s, fmt='%Y:%m:%d %H:%M:%S'):
    """
    The format of datetime in exif is as follows:
        %Y:%m:%d %H:%M:%S
    Convert the string with this format to a datetime object.
    """
    if not s:
        return None
    try:
        return datetime.strptime(s, fmt)
    except ValueError:
        return None

@register.filter_function
def in_group(user, group):
    if group:
        if isinstance(user, AnonymousUser):
            return False
        return group in [dict['pk'] for dict in user.group_set.values('pk')]
    else:
        return False

@register.filter
def domain(link):
    from urllib.parse import urlparse
    link = urlparse(link)
    return link.hostname

@register.filter
def strip_template_tags(string):
    p = re.compile(r'{[#{%][^#}%]+[%}#]}')
    return re.sub(p, '', string)

@register.filter
@stringfilter
def stripentities(value):
    """Strips all [X]HTML entities."""
    return strip_entities(value)
stripentities.is_safe = True

@register.filter
@stringfilter
def striphtml(value):
    """Strips all [X]HTML tags and entities."""
    return strip_html(value)
striphtml.is_safe = True

@register.filter
def format_currency(value):
    """format currency"""
    from tendenci.apps.base.utils import tcurrency
    return tcurrency(value)
format_currency.is_safe = True

@register.filter
def get_object(obj):
    """return obj.object if this obj has the attribute of object"""
    if hasattr(obj, 'object'):
        return obj.object
    else:
        return obj

@register.filter
def scope(object):
    return dir(object)

@register.filter
def obj_type(object):
    """
    Return object type
    """
    return type(object)

@register.filter
def is_iterable(object):
    """
    Return boolean
    Is the object iterable or not
    """
    try:
        iter(object)
        return True
    except TypeError:
        return False

@register.filter
@stringfilter
def basename(path):
    from os.path import basename
    return basename(path)

@register.filter
def date_diff(value, date_to_compare=None):
    """Compare two dates and return the difference in days"""
    import datetime
    if not isinstance(value, datetime.datetime):
        return 0

    if not isinstance(date_to_compare, datetime.datetime):
        date_to_compare = datetime.datetime.now()

    return (date_to_compare - value).days

@register.filter
def first_chars(string, arg):
    """ returns the first x characters from a string """
    string = str(string)
    if arg:
        if not arg.isdigit():
            return string
        return string[:int(arg)]
    else:
        return string
    return string

@register.filter
def rss_date(value, arg=None):
    """Formats a date according to the given format."""
    from django.utils import formats
    from django.utils.dateformat import format
    from datetime import datetime

    if not value:
        return u''
    else:
        value = datetime(*value[:-3])
    if arg is None:
        arg = settings.DATE_FORMAT
    try:
        return formats.date_format(value, arg)
    except AttributeError:
        try:
            return format(value, arg)
        except AttributeError:
            return ''
rss_date.is_safe = False

@register.filter()
def obfuscate_email(email, linktext=None, autoescape=None):
    """
    Given a string representing an email address,
    returns a mailto link with rot13 JavaScript obfuscation.

    Accepts an optional argument to use as the link text;
    otherwise uses the email address itself.
    """
    if autoescape:
        esc = conditional_escape
    else:
        def esc(x):
            return x

    email = re.sub(r'@', r'\\100', re.sub(r'\.', r'\\056', esc(email)))
    email = codecs.encode(email, 'rot13')

    if linktext:
        linktext = esc(linktext).encode('unicode-escape').decode()
        linktext = codecs.encode(linktext, 'rot13')
    else:
        linktext = email

    rotten_link = """<script type="text/javascript">document.write \
        ("<n uers=\\\"znvygb:%s\\\">%s<\\057n>".replace(/[a-zA-Z]/g, \
        function(c){return String.fromCharCode((c<="Z"?90:122)>=\
        (c=c.charCodeAt(0)+13)?c:c-26);}));</script>""" % (email, linktext)
    return mark_safe(rotten_link)
obfuscate_email.needs_autoescape = True

@register.filter_function
def split_str(s, args):
    """
    Split a string using the python string split method
    """
    if args:
        if isinstance(s, str):
            splitter = args[0]
            return s.split(splitter)
        return s
    return s

@register.filter_function
def str_basename(s):
    """
    Get the basename using the python basename method
    """
    return basename(s)

@register.filter
@stringfilter
def twitterize(value, autoescape=None):
    value = strip_tags(value)
    # Link URLs
    value = urlize(value, nofollow=False, autoescape=autoescape)

    # Link twitter usernames for the first person
    value = re.sub(r'(^[^:]+)', r'<a href="http://twitter.com/\1">\1</a>', value)
    # Link twitter usernames prefixed with @
    value = re.sub(r'(\s+|\A)@([a-zA-Z0-9\-_]*)\b', r'\1<a href="http://twitter.com/\2">@\2</a>', value)
    # Link hash tags
    value = re.sub(r'(\s+|\A)#([a-zA-Z0-9\-_]*)\b', r'\1<a href="http://search.twitter.com/search?q=%23\2">#\2</a>', value)
    return mark_safe(value)
twitterize.is_safe = True
twitterize.needs_autoescape = True

@register.filter
@stringfilter
def twitterdate(value):
    from datetime import datetime, timedelta
    time = value.replace(" +0000", "")
    dt = datetime.strptime(time, "%a, %d %b %Y %H:%M:%S")
    return dt + timedelta(hours=-6)


@register.filter
def thumbnail(file, size='200x200'):
    # defining the size
    x, y = [int(x) for x in size.split('x')]
    # defining the filename and the miniature filename
    filehead, filetail = os.path.split(file.name)
    basename, format = os.path.splitext(filetail)
    miniature = basename + '_' + size + format
    filename = file.name
    miniature_filename = os.path.join(filehead, miniature)
    filehead, filetail = os.path.split(file.url)
    miniature_url = filehead + '/' + miniature

    thumbnail_exist = False
    if default_storage.exists(miniature_filename):
        mt_filename = default_storage.get_modified_time(filename)
        mt_miniature_filename = default_storage.get_modified_time(
                                                miniature_filename)
        if mt_filename > mt_miniature_filename:
            # remove the miniature
            default_storage.delete(miniature_filename)
        else:
            thumbnail_exist = True

    # if the image wasn't already resized, resize it
    if not thumbnail_exist:

        if not default_storage.exists(filename):
            return u''

        image = Image.open(default_storage.open(filename))
        image.thumbnail([x, y], Image.ANTIALIAS)

        f = default_storage.open(miniature_filename, 'w')
        image.save(f, image.format, quality=90, optimize=1)
        f.close()

    return miniature_url

@register.filter_function
def datedelta(dt, range_):
    from datetime import timedelta

    range_type = 'add'
    # parse the range
    if '+' in range_:
        range_ = range_[1:len(range_)]
    if '-' in range_:
        range_type = 'subtract'
        range_ = range_[1:len(range_)]
    k, v = range_.split('=')
    set_range = {
        str(k): int(v)
    }

    # set the date
    if range_type == 'add':
        dt = dt + timedelta(**set_range)
    if range_type == 'subtract':
        dt = dt - timedelta(**set_range)

    return dt

@register.filter
def split(str, splitter):
    return str.split(splitter)

@register.filter
def tag_split(str):
    str = "".join(str)
    str = str.replace(", ", ",")
    return str.split(",")

@register.filter
def make_range(value):
    try:
        value = int(value)
        if value > 0:
            return list(range(int(value)))
        return []
    except:
        return []

@register.filter
def underscore_space(value):
    return value.replace("_", " ")

@register.filter
def format_string(value, arg):
    return arg % value

@register.filter
def md5_gs(value, arg=None):
    import hashlib
    from datetime import datetime, timedelta

    hashdt = ''
    if arg and int(arg):
        timestamp = datetime.now() + timedelta(hours=int(arg))
        hashdt = hashlib.md5(timestamp.strftime("%Y;%m;%d;%H;%M").replace(';0', ';').encode()).hexdigest()
    return ''.join([value, hashdt])

@register.filter
def multiply(value, arg):
    return Decimal(str(value)) * Decimal(str(arg))

@register.filter
def add_decimal(value, arg):
    return Decimal(str(value)) + Decimal(str(arg))

@register.filter
def phonenumber(value):
    if value:
        # split number from extension or any text
        x = re.split(r'([a-zA-Z]+)', value)
        # clean number
        y = ''.join(i for i in x[0] if i.isdigit())

        if len(y) > 10:    # has country code
            code = y[:len(y)-10]
            number = y[len(y)-10:]
            if code == '1':
                number = "(%s) %s-%s" %(number[:3], number[3:6], number[6:])
            else:
                number = "+%s %s %s %s" %(code, number[:3], number[3:6], number[6:])
        else:    # no country code
            number = "(%s) %s-%s" %(y[:3], y[3:6], y[6:])

        # attach additional text extension
        ext = ''
        for i in range(1, len(x)):
            ext = ''.join((ext, x[i]))
        if ext:
            return ' '.join((number, ext))
        else:
            return number


@register.filter
def timezone_label(value):
    try:
        now = datetime.now(pytz.timezone(value))
        tzinfo = now.strftime("%z")
        return "(GMT%s) %s" %(tzinfo, value)
    except:
        return ""

@register.filter
def field_to_string(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        if len(value) == 0:
            return ""
        if len(value) == 1:
            return str(value[0])
        if len(value) == 2:
            return "%s and %s" % (value[0], value[1])
        return ", ".join(value)
    return str(value)


@register.filter
def url_complete(value):
    """prepend https:// if missing"""
    if 'https://' not in value and 'http://' not in value:
        return 'https://' + value
    return value
