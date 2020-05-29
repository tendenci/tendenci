from builtins import object, str
import os
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import codecs
import csv
import hashlib
import hmac
import base64
from urllib.request import Request, build_opener
from urllib.parse import urlparse
import pytz
import socket
from PIL import Image
from io import BytesIO, StringIO
import requests
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from PIL import Image as pil
from PIL import ImageFile

from django.conf import settings
from django.utils import translation
from django.template.defaultfilters import slugify
from django.core.files.storage import default_storage
from django.core.validators import validate_email as _validate_email
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.contrib.admin.utils import NestedObjects
from django.utils.functional import keep_lazy_text
from django.utils.text import capfirst, Truncator
from django.utils.encoding import smart_str
from django.db import router
from django.utils.encoding import force_text
from django.contrib.auth import get_permission_codename
from django.utils.html import format_html, strip_tags
from django.utils.translation import ugettext as _
from django.core.validators import EmailValidator

from django.utils.functional import Promise
from django.core.serializers.json import DjangoJSONEncoder

from simple_salesforce import Salesforce

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.utils import get_theme_root

ImageFile.LOAD_TRUNCATED_IMAGES = True

STOP_WORDS = ['able','about','across','after','all','almost','also','am',
              'among','an','and','any','are','as','at','be','because',
              'been','but','by','can','cannot','could','dear','did','do',
              'does','either','else','ever','every','for','from','get',
              'got','had','has','have','he','her','hers','him','his','how',
              'however','i','if','in','into','is','it','its','just','least',
              'let','like','likely','may','me','might','most','must','my',
              'neither','no','nor','not','of','off','often','on','only','or',
              'other','our','own','rather','said','say','says','she','should',
              'since','so','some','than','that','the','their','them','then',
              'there','these','they','this','tis','to','too','twas','us','wants',
              'was','we','were','what','when','where','which','while','who',
              'whom','why','will','with','would','yet','you','your',
              'find','very','still','non','here', 'many', 'a','s','t','ve',
              'use', 'don\'t', 'can\'t', 'wont', 'come','you\'ll', 'want']


ORIENTATION_EXIF_TAG_KEY = 274


def is_valid_domain(email_domain):
    """
    Check if it's a valid email domain.
    """
    if '@' in email_domain:
        email_domain = email_domain.rsplit('@', 1)[1]
    return EmailValidator().validate_domain_part(email_domain)


def google_cmap_sign_url(url):
    """ Signs a URL and returns the URL with digital signature for Google static maps API.

    For the detailed guides to generating a digital signature, go to:
    https://developers.google.com/maps/documentation/static-maps/get-api-key#digital-signature
    """
    if not url:
        raise Exception('A url is required.')

    signing_secret = settings.GOOGLE_SMAPS_URL_SIGNING_SECRET
    if not signing_secret:
        return url

    url_parts = urlparse(url)
    if not url_parts.query:
        return url

    # don't sign if api key is not provided
    if 'key' not in dict([x.split('=') for x in url_parts.query.split('&')]):
        return url

    # strip off the domain portion of the request, leaving only the path and the query
    url_parts_to_sign = url_parts.path + "?" + url_parts.query

    # retrieve the URL signing secret by decoding it - it is encoded in a modified Base64
    decoded_signing_secret = base64.urlsafe_b64decode(signing_secret.encode())

    # sign it  using the HMAC-SHA1 algorithm
    signature = hmac.new(decoded_signing_secret, url_parts_to_sign.encode(), hashlib.sha1)

    # encode the resulting binary signature using the modified Base64 for URLs
    # to convert this signature into something that can be passed within a URL
    encoded_signature = base64.urlsafe_b64encode(signature.digest())

    # append digital signature
    return url + "&signature=" + encoded_signature.decode()


class LazyEncoder(DjangoJSONEncoder):
    """
    Encodes django's lazy i18n strings.
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


def get_languages_with_local_name():
    """
    Get a list of tuples of available languages with local name.
    """
    return [(ll['code'], '%s (%s)' % (ll['name_local'], ll['code'])) for ll in
            [translation.get_language_info(l[0])
             for l in settings.LANGUAGES]]


def get_deleted_objects(objs, user):
    """
    Find all objects related to ``objs`` that should also be deleted. ``objs``
    must be a homogeneous iterable of objects (e.g. a QuerySet).

    Returns a nested list of strings suitable for display in the
    template with the ``unordered_list`` filter.

    Copied and updated from django.contrib.admin.utils for front end display.
    """
    using = router.db_for_write(objs[0].__class__)
    collector = NestedObjects(using=using)
    collector.collect(objs)
    perms_needed = set()

    def format_callback(obj):
        opts = obj._meta

        no_edit_link = '%s: %s' % (capfirst(opts.verbose_name),
                                   force_text(obj))

        p = '%s.%s' % (opts.app_label,
                           get_permission_codename('delete', opts))
        if not user.has_perm(p):
            perms_needed.add(opts.verbose_name)

        if hasattr(obj, 'get_absolute_url'):
            url = obj.get_absolute_url()
            # Display a link to the admin page.
            return format_html('{}: <a href="{}">{}</a>',
                               capfirst(opts.verbose_name),
                               url,
                               obj)
        else:
            # Don't display link to edit, because it either has no
            # admin or is edited inline.
            return no_edit_link

    to_delete = collector.nested(format_callback)

    protected = [format_callback(obj) for obj in collector.protected]
    model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}

    return to_delete, model_count, perms_needed, protected


def get_timezone_choices():
    choices = []
    for tz in pytz.common_timezones:
        ofs = datetime.now(pytz.timezone(tz)).strftime("%z")
        choices.append((int(ofs), tz, "(GMT%s) %s" % (ofs, tz)))
    choices.sort()
    return [t[1:] for t in choices]


def adjust_datetime_to_timezone(value, from_tz, to_tz=None):
    """
    Given a ``datetime`` object, adjust it according to the from_tz timezone
    string into the to_tz timezone string.
    """
    if to_tz is None:
        to_tz = settings.TIME_ZONE
    if value.tzinfo is None:
        if not hasattr(from_tz, "localize"):
            from_tz = pytz.timezone(smart_str(from_tz))
        value = from_tz.localize(value)
    return value.astimezone(pytz.timezone(smart_str(to_tz)))


def localize_date(date, from_tz=None, to_tz=None):
    """
        Takes the given date/timezone
        and converts it to the sites date/timezone

        localize_date(date, from_tz, to_tz=None)
    """

    # set the defaults
    if from_tz is None:
        from_tz=settings.TIME_ZONE

    if to_tz is None:
        to_tz=settings.TIME_ZONE

    return adjust_datetime_to_timezone(date,from_tz=from_tz,to_tz=to_tz)


def tcurrency(mymoney):
    """
        format currency - GJQ
        ex: 30000.232 -> $30,000.23
            -30000.232 -> $(30,000.23)
    """
    if mymoney is None:
        return 'n/a'
    
    currency_symbol = get_setting("site", "global", "currencysymbol")
    allow_commas = get_setting("site", "global", "allowdecimalcommas")

    if not currency_symbol:
        currency_symbol = "$"

    if not isinstance(mymoney, str):
        if mymoney >= 0:
            fmt = '%s%s'
        else:
            fmt = '%s(%s)'
        if allow_commas:
            mymoney = intcomma(mymoney)
        return fmt % (currency_symbol, mymoney)
    else:
        return mymoney


def currency_check(mymoney):
    """
    Clear out dollar symbols and commas, and convert it to Decimal
    """
    if mymoney:
        mymoney = mymoney.replace('$', '').replace(',', '')
    else:
        mymoney = 0
    mymoney = Decimal(mymoney)

    return mymoney


def format_datetime_range(start_dt, end_dt, format_date='%A, %B %d, %Y', format_time='%I:%M %p'):
    """
        takes datetime objects, start_dt, end_dt and format (for date and time)
        returns a formated datetime string with range.
        ex:
            dt_str = format_datetime_range(datetime(2010, 8, 12, 8, 30, 0),
                                           datetime(2010, 8, 12, 17, 30, 0))
            # returns: Thursday, August 12, 2010 8:30 AM - 05:30 PM
                                                                    - GJQ 8/12/2010
    """
    if isinstance(start_dt, datetime) and isinstance(end_dt, datetime):
        if start_dt.date() == end_dt.date():
            return '%s %s - %s' % (start_dt.strftime(format_date),
                                   start_dt.strftime(format_time),
                                   end_dt.strftime(format_time))
        else:
            return '%s %s - %s %s' % (start_dt.strftime(format_date),
                                      start_dt.strftime(format_time),
                                      end_dt.strftime(format_date),
                                      end_dt.strftime(format_time))


def day_validate(dt, day):
    """
        validate if this day is valid in the month of dt, and correct it if not.
    """
    if isinstance(dt, datetime):
        try:
            day = int(day)
        except:
            day = 1

        if day == 0: day = 1

        # the last day of this month
        last_day_of_month = (datetime(dt.year, dt.month, 1) + relativedelta(months=1) - timedelta(days=1)).day

        # if last_day_of_month = 31 and day = 32, set day = 31
        if day > last_day_of_month:
            day = last_day_of_month
    return day


def get_unique_username(user):
    import uuid
    from django.contrib.auth.models import User
    if not user.username:
        if user.email:
            user.username = user.email
    if not user.username:
        if user.first_name and user.last_name:
            user.username = '%s%s' % (user.first_name[0], user.last_name)
    if not user.username:
        user.username = str(uuid.uuid4())[:7]
    if len(user.username) > 20:
        user.username = user.username[:7]

    # check if this username already exists
    users = User.objects.filter(username__istartswith=user.username)

    if users:
        t_list = [u.username[len(user.username):] for u in users]
        num = 1
        while str(num) in t_list:
            num += 1

        user.username = '%s%s' % (user.username, str(num))

    return user.username


def send_email_notification(notice_name, recipients, extra_context):
    """
    Send email notice specified by the notice_name to the recipients.
    recipients - a list of emails
    """
    try:
        from tendenci.apps.notifications import models as notification
    except:
        notification = None
    if notification and recipients:
        notification.send_emails(recipients, notice_name, extra_context)


def generate_meta_keywords(value):
    """
        Take any string and removes the html and html entities
        and then runs a keyword density analyizer on the text
        to decided the 20 best one word and two word
        key phrases
    """
    try:
        from re import compile
        from operator import itemgetter

        from django.utils.text import unescape_entities
        from django.utils.translation import ugettext_lazy as _

        # translate the stop words
        TR_STOP_WORDS = _(' '.join(STOP_WORDS))
        TR_STOP_WORDS = TR_STOP_WORDS.split()

        # get rid of the html tags
        value = strip_tags(value)

        # get rid of the html entities
        value = unescape_entities(value)

        # lower case the value
        value = value.lower()

        # get the one word, two word, and three word patterns
        one_word_pattern = compile(r'\s*(\w+[a-zA-Z0-9:\-]*\w*(\'\w{1,2})?)')
        two_word_pattern = compile(r'\s*(\w+[a-zA-Z0-9:\-]*\w*(\'\w{1,2})?)(\s+|_)(\w+[a-zA-Z0-9:\-]*\w*(\'\w{1,2})?)')

        # get the length of the value
        value_length = len(value)

        # make a list of one words
        search_end = 0
        one_words = []
        while search_end < value_length:
            s = one_word_pattern.search(value, search_end)
            if s:
                one_word = s.group(1)
                # remove the : from the word
                if one_word[-1] == ':':
                    one_word = one_word[:-1]

                one_words.append(one_word)
                search_end = s.end()
            else: break

        # remove the stop words
        one_words = [word for word in one_words if word not in TR_STOP_WORDS]

        # get the density, and word into a tuple
        one_words_length = len(one_words)
        unique_words = set(word for word in one_words)
        one_words = [(word, round((one_words.count(word)*100.00/one_words_length),2)) for word in unique_words]

        # sort the tuple by the density
        one_words = sorted(one_words, key=itemgetter(1), reverse=True)

        # get the 10 best keywords
        one_words = [word[0] for word in one_words[:10]]

        # make a list of two words phrases without stop phrases
        search_end = 0
        two_words = []
        while search_end < value_length:
            s = two_word_pattern.search(value, search_end)
            if s:
                word1 = s.group(1)
                word2 = s.group(4)
                # remove the : from the words
                if word1[-1] == ':':
                    word1 = word1[:-1]
                if word2[-1] == ':':
                    word2 = word2[:-1]

                if word1 not in TR_STOP_WORDS:
                    if word2 not in TR_STOP_WORDS:
                        two_word = word1 + ' ' + word2
                        two_words.append(two_word)

                search_start = s.start()
                next_search = one_word_pattern.search(value, search_start)
                search_end = next_search.end()
            else:
                # if no match, advance a word
                s = one_word_pattern.search(value, search_end)
                if s:
                    search_end = s.end()
                else: search_end = value_length

        # get the density, and word into a tuple
        two_words_length = len(two_words)
        unique_words = set(words for words in two_words)
        two_words = [(words, round((two_words.count(words)*100.00/two_words_length),2)) for words in unique_words]

        # sort the tuple by the density
        two_words = sorted(two_words, key=itemgetter(1), reverse=True)

        # get the best 2 word keywords
        two_words = [word[0] for word in two_words[:10]]

        # add the two lists together
        keywords = two_words + one_words

        return ','.join(keywords)
    except AttributeError:
        return ''


def filelog(*args, **kwargs):
    """
        Will generate a file with output to the
        PROJECT_ROOT

        filelog(args...Nargs)
        filelog(args, mode='a+', filename='log.txt', path=path)
    """
    if 'path' in kwargs:
        path = kwargs['path']
    else:
        path = settings.PROJECT_ROOT

    if 'filename' in kwargs:
        filename = kwargs['filename']
    else:
        filename = 'filelog.txt'

    if 'mode' in kwargs:
        mode = kwargs['mode']
    else:
        mode = 'a+'

    f = open(path + '/%s' % filename, mode)
    for arg in args:
        f.write(arg)
    f.close()


class FormDateTimes(object):
    """
        Object that creates the start and end dates and times
        for a form that needs them
    """
    def __init__(self, start_dt=None, end_dt=None):
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.get_date_times()
    def get_date_times(self):
        if self.start_dt is None:
            self.start_dt = datetime.now()

        # remove the seconds and microseconds
        self.start_dt = self.start_dt.replace(second=00,microsecond=00)

        # check if its past the half hour or before and increment the time.
        if self.start_dt.minute > 0 and self.start_dt.minute < 30:
            self.start_dt = self.start_dt.replace(minute=30)
        if self.start_dt.minute > 30:
            if self.start_dt.hour >= 23:
                self.start_dt = self.start_dt.replace(hour=00)
            else:
                self.start_dt = self.start_dt.replace(hour=self.start_dt.hour+1)

            self.start_dt = self.start_dt.replace(minute=00)

        # set the end time to an hour ahead
        self.end_dt = self.start_dt + timedelta(hours=1)
date_times = FormDateTimes()


def enc_pass(password):
    from base64 import urlsafe_b64encode
    return ''.join(list(reversed(urlsafe_b64encode(password.encode()).decode())))


def dec_pass(password):
    from base64 import urlsafe_b64decode

    pw_list = list(str(password))
    pw_list.reverse()

    return urlsafe_b64decode(''.join(pw_list).encode()).decode()


def url_exists(url):
    o = urlparse(url)

    if not o.scheme:
        # doesn't have a scheme, relative url
        url = '%s%s' %  (get_setting('site', 'global', 'siteurl'), url)

    r = requests.head(url)
    return r.status_code == 200


def parse_image_sources(string):
    p = re.compile(r'<img[^>]* src=\"([^\"]*)\"[^>]*>')
    image_sources = re.findall(p, string)
    return image_sources


def make_image_object_from_url(image_url):
    # parse url
    parsed_url = urlparse(image_url)

    # handle absolute and relative urls, Assuming http for now.
    if not parsed_url.scheme:
        image_url = '%s%s' %  (get_setting('site', 'global', 'siteurl'), image_url)

    request = Request(image_url)
    request.add_header('User-Agent', settings.TENDENCI_USER_AGENT)
    opener = build_opener()

    # make image object
    try:
        socket.setdefaulttimeout(1.5)
        data = opener.open(request).read() # get data
        im = Image.open(BytesIO(data))
    except:
        im = None
    return im


def apply_orientation(im):
    """
    Some photos are taken with camera rotated. The rotated info is stored in the EXIF metadata.
    But EXIF metadata gets lost when an image is cropped or modified, which can lead to unintended
    position.

    Extract the orientation info and apply the rotation if needed (before cropping or modifying an image).

    Parameters
    -----------
    im : Image
        An Image instance
    
    Returns
    -------
    Image 
        A rotated or original image instance
    """

    try:
        if hasattr(im, '_getexif'): # only present in JPEGs
            image_exif = im._getexif()       # returns None if no EXIF data
            if image_exif is not None:
                image_orientation = image_exif.get(ORIENTATION_EXIF_TAG_KEY)
                if image_orientation:
                    if image_orientation == 3:
                        return im.rotate(180)
                    if image_orientation == 6:
                        return im.rotate(-90)
                    if image_orientation == 8:
                        return im.rotate(90)
    except:
        pass 
    return im

def image_rescale(img, size, force=True):
    """Rescale the given image, optionally cropping it to make sure the result image has the specified width and height."""
    format = img.format  # temp. save format
    max_width, max_height = size

    if not force:
        img.thumbnail((max_width, max_height), pil.ANTIALIAS)
    else:
        src_width, src_height = img.size
        src_ratio = float(src_width) / float(src_height)
        dst_width, dst_height = max_width, max_height
        dst_ratio = float(dst_width) / float(dst_height)

        if dst_ratio < src_ratio:
            crop_height = src_height
            crop_width = crop_height * dst_ratio
            x_offset = float(src_width - crop_width) / 2
            y_offset = 0
        else:
            crop_width = src_width
            crop_height = crop_width / dst_ratio
            x_offset = 0
            y_offset = float(src_height - crop_height) / 3
        img = img.crop((int(x_offset), int(y_offset), int(x_offset)+int(crop_width), int(y_offset)+int(crop_height)))
        img = img.resize((dst_width, dst_height), pil.ANTIALIAS)

    img.format = format  # add format back
    return img


def in_group(user, group):
    """
        Tells you if a user is in a particular group
        in_group(user,'administrator')
        returns boolean
    """
    return user.groups.filter(id=group.id).exists()


def detect_template_tags(string):
    """
        Used to detect wether or not any string contains
        template tags in the system
        returns boolean
    """
    p = re.compile(r'{[#{%][^#}%]+[%}#]}', re.IGNORECASE)
    return p.search(string)


def get_template_list():
    """
    Get a list of files from the template
    directory that begin with 'default-'
    """
    file_list = []
    theme_dir = get_theme_root()
    template_dir = os.path.join(theme_dir, 'templates')

    if os.path.isdir(template_dir):
        item_list = os.listdir(template_dir)
    else:
        item_list = []

    for item in item_list:
        current_item = os.path.join(template_dir, item)
        path_split = os.path.splitext(current_item)
        extension = path_split[1]
        base_name = os.path.basename(path_split[0])
        if os.path.isfile(current_item):
            if extension == ".html" and "default-" in base_name:
                base_display_name = base_name[8:].replace('-',' ').title()
                file_list.append((item,base_display_name,))
    return sorted(file_list)


def template_exists(template):
    """
    Check if the template exists
    """
    try:
        get_template(template)
    except (TemplateDoesNotExist, IOError):
        return False
    return True


def fieldify(s):
    """Convert the fields in the square brackets to the django field type.

        Example: "[First Name]: Lisa"
                    will be converted to
                "{{ first_name }}: Lisa"
    """
    #p = re.compile(r'(\[([\w\d\s_-]+)\])')
    p = re.compile(r'(\[(.*?)\])')
    return p.sub(slugify_fields, s)


def slugify_fields(match):
    return '{{ %s }}' % (slugify(match.group(2))).replace('-', '_')


entities_re = re.compile(r'&(?:\w+|#\d+);')
@keep_lazy_text
def strip_entities(value):
    """Returns the given HTML with all entities (&something;) stripped."""
    # This was copied from Django 1.9 since it is removed in Django 1.10
    return entities_re.sub('', force_text(value))


def strip_html(value):
    """Returns the given HTML with all tags and entities stripped."""
    return strip_entities(strip_tags(value))


def convert_absolute_urls(content, base_url):
    """
    Convert the relative urls in the content to the absolute urls.
    """
    content = content.replace('src="/', 'src="%s/' % base_url)
    content = content.replace('href="/', 'href="%s/' % base_url)
    return content


def is_blank(item):
    """
    Check if values inside list are blank
    Check if values inside dictionary are blank.
    """
    if isinstance(item, dict):
        l = list(item.values())
    elif isinstance(item, list):
        l = item
    elif isinstance(item, str):
        l = list(item)

    item = []

    # return not bool([i for i in l if i.strip)
    return not any(l)
    #return not bool(''.join(l).strip())

    raise Exception


def normalize_newline(file_path):
    """
    Normalize the new lines for a file ```file_path```

    ```file_path``` is a relative path.
    """
    data = default_storage.open(file_path).read().decode('utf-8')
    data = data.replace('\r\n', '\n').replace('\r', '\n')
    f = default_storage.open(file_path, 'w')
    f.write(data)
    f.close()


def get_pagination_page_range(num_pages, max_num_in_group=10,
                              start_num=35, curr_page=1):
    """
    Calculate the pagination page range to display.
    Display the page links in 3 groups.
    """
    if num_pages > start_num:
        # first group
        page_range = list(range(1, max_num_in_group + 1))
        # middle group
        i = curr_page - int(max_num_in_group / 2)
        if i <= max_num_in_group:
            i = max_num_in_group
        else:
            page_range.extend(['...'])
        j = i + max_num_in_group
        if j > num_pages - max_num_in_group:
            j = num_pages - max_num_in_group
        page_range.extend(list(range(i, j)))
        if j < num_pages - max_num_in_group:
            page_range.extend(['...'])
        # last group
        page_range.extend(list(range(num_pages - max_num_in_group,
                                     num_pages + 1)))
    else:
        page_range = list(range(1, num_pages + 1))
    return page_range


class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.reader).encode("utf-8")


class UnicodeReader(object):
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def __next__(self):
        row = next(self.reader)
        return [str(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow(row)
        # Fetch output from the queue ...
        data = self.queue.getvalue()
        # ... and encode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def get_salesforce_access():

    required_settings = (hasattr(settings, 'SALESFORCE_USERNAME'),
                         hasattr(settings, 'SALESFORCE_PASSWORD'),
                         hasattr(settings, 'SALESFORCE_SECURITY_TOKEN'))

    is_sandbox = getattr(settings, 'SALESFORCE_SANDBOX', False)

    if all(required_settings):
        try:
            sf = Salesforce(username=settings.SALESFORCE_USERNAME,
                            password=settings.SALESFORCE_PASSWORD,
                            security_token=settings.SALESFORCE_SECURITY_TOKEN,
                            sandbox=is_sandbox)
            return sf
        except:
            print('Salesforce authentication failed')

    return None


def create_salesforce_contact(profile):

    if hasattr(settings, 'SALESFORCE_AUTO_UPDATE') and settings.SALESFORCE_AUTO_UPDATE:
        sf = get_salesforce_access()

        if profile.sf_contact_id:
            # sf_contact_id might be deleted at saleforce end, check for existence
            result = sf.query("SELECT FirstName, LastName, Email FROM Contact WHERE Id='%s'" % profile.sf_contact_id)
            if 'records' in result and result['records']:
                return profile.sf_contact_id

        # Make sure that user last name is not blank
        # since that is a required field for Salesforce Contact.
        user = profile.user
        if sf and user.last_name:
            # Query for a duplicate entry in salesforce
            # saleforce blocks the request if email is already in their system - so just checking email
            if user.email:
                result = sf.query("SELECT Id FROM Contact WHERE Email='%s'" % user.email.replace("'", "''"))
                if result['records']:
                    return result['records'][0]['Id']

                contact = sf.Contact.create({
                    'FirstName':user.first_name,
                    'LastName':user.last_name,
                    'Email':user.email,
                    'Title':profile.position_title,
                    'Phone':profile.phone,
                    'MailingStreet':profile.address,
                    'MailingCity':profile.city,
                    'MailingState':profile.state,
                    'MailingCountry':profile.country,
                    'MailingPostalCode':profile.zipcode,
                    })

                # update field Company_Name__c
                if profile.company and 'Company_Name__c' in contact:
                    sf.Contact.update(contact['id'], {'Company_Name__c': profile.company})

                profile.sf_contact_id = contact['id']
                profile.save()
                return contact['id']
    return None


def directory_cleanup(dir_path, ndays):
    """
    Delete the files that are older than 'ndays' in the directory 'dir_path'
    The 'dir_path' should be a relative path. We cannot use os.walk.
    """
    if not default_storage.exists(dir_path):
        return

    foldernames, filenames = default_storage.listdir(dir_path)
    for filename in filenames:
        if not filename:
            continue
        file_path = os.path.join(dir_path, filename)
        modified_dt = default_storage.get_modified_time(file_path)
        if modified_dt + timedelta(days=ndays) < datetime.now():
            # the file is older than ndays, delete it
            default_storage.delete(file_path)
    for foldername in foldernames:
        folder_path = os.path.join(dir_path, foldername)
        directory_cleanup(folder_path, ndays)


def checklist_update(key):
    from tendenci.apps.base.models import ChecklistItem
    try:
        item = ChecklistItem.objects.get(key=key)
    except ChecklistItem.DoesNotExist:
        return None

    if not item.done:
        item.done = True
        item.save()


def extract_pdf(fp):
    """
    Extract text from PDF file.
    """
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    text_content = [] # a list of strings, each representing text collected from each page of the pdf
    for page in PDFPage.create_pages(PDFDocument(PDFParser(fp))):
        interpreter.process_page(page) # LTPage object for this page
        layout = device.get_result() # layout is an LTPage object which may contain child objects
        for lt_obj in layout: # extract text from text objects
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                if isinstance(lt_obj.get_text(), str):
                    text_content.append(lt_obj.get_text())
                else:
                    text_content.append(lt_obj.get_text().decode())
    device.close()
    return '\n\n'.join(text_content)


def normalize_field_names(fieldnames):
    for i in range(0, len(fieldnames)):
        # clean up the fieldnames
        # ex: change First Name to first_name
        fieldnames[i] = fieldnames[i].lower().replace(' ', '_')

    return fieldnames


@keep_lazy_text
def truncate_words(s, num, end_text='...'):
    truncate = end_text and ' %s' % end_text or ''
    return Truncator(s).words(num, truncate=truncate)


def validate_email(s, quiet=True):
    try:
        _validate_email(s)
        return is_valid_domain(s)
    except Exception as e:
        if not quiet:
            raise e
    return False


def get_latest_version():
    from xmlrpc import client as xmlrpc_client
    with xmlrpc_client.ServerProxy('http://pypi.python.org/pypi') as proxy:
        return proxy.package_releases('tendenci')[0]


def add_tendenci_footer(email_content, content_type='html'):
    if content_type == 'text':
        footer = _("This Association is Powered by Tendenci - The Open Source AMS https://www.tendenci.com")
        return email_content + '\n\n' + footer
    # Sorry but have to put html code here instead of in a template
    footer = '''<br /><div style="text-align:center; font-size:90%;">
    {0} <a href="https://www.tendenci.com" style="text-decoration: none;">{1}</a>
    <div>
    <div style="margin:5px auto;">
    <a href="https://www.tendenci.com" style="text-decoration: none;">
    <img src="https://www.tendenci.com/media/tendenci-os-ams.jpg" width="100" height="29" alt="tendenci logo" />
    </a>
    </div>'''.format(_('This Association is Powered by'), _('Tendenci &ndash; The Open Source AMS'))
    if email_content.find('</body>') != -1:
        return email_content.replace("</body>", footer + "\n</body>")
    return email_content + footer


def correct_filename(filename):
    """
    Renames filename if needed -  replaces dots, underscores, and spaces with dashes.
    And changes filename to lowercase.
    """
    root, ext = os.path.splitext(filename)
    root = (re.sub(r'[^a-zA-Z0-9]+', '-', root)).lower()
    return root + ext
