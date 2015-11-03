import os
import re
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import codecs
import cStringIO
import csv
import chardet
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

from django.conf import settings
from django.utils import translation
from django.template.defaultfilters import slugify
from django.core.files.storage import default_storage
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.contrib.admin.util import NestedObjects
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.encoding import force_unicode
from django.db import router

from simple_salesforce import Salesforce

from tendenci.core.base.models import ChecklistItem
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.theme.utils import get_theme_root

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

template_directory = "templates"
THEME_ROOT = get_theme_root()

def get_languages_with_local_name():
    """
    Get a list of tuples of available languages with local name.
    """
    return [(ll['code'], '%s (%s)' % (ll['name_local'], ll['code'])) for ll in
            [translation.get_language_info(l[0])
             for l in settings.LANGUAGES]] 
    

def get_deleted_objects(obj, user):
    """
    Find all objects related to ``obj`` that should also be deleted.

    Returns a nested list of strings suitable for display in the
    template with the ``unordered_list`` filter.

    Copied and updated from django.contrib.admin.util for front end display.

    """
    using = router.db_for_write(obj.__class__)
    collector = NestedObjects(using=using)
    collector.collect([obj])
    perms_needed = set()

    def format_callback(obj):
        opts = obj._meta

        if hasattr(obj, 'get_absolute_url'):
            url = obj.get_absolute_url()
            p = '%s.%s' % (opts.app_label,
                           opts.get_delete_permission())
            if not user.has_perm(p):
                perms_needed.add(opts.verbose_name)
            # Display a link to the admin page.
            return mark_safe(u'%s: <a href="%s">%s</a>' %
                             (escape(capfirst(opts.verbose_name)),
                              url,
                              escape(obj)))
        else:
            # no link
            return u'%s: %s' % (capfirst(opts.verbose_name),
                                force_unicode(obj))

    to_delete = collector.nested(format_callback)

    protected = [format_callback(obj) for obj in collector.protected]

    return to_delete, perms_needed, protected


# this function is not necessary - datetime.now() *is* localized in django
def now_localized():
    from timezones.utils import adjust_datetime_to_timezone
    from time import strftime, gmtime

    os_timezone = strftime('%Z',gmtime())
    if os_timezone == 'CST': os_timezone = 'US/Central'
    django_timezone =  settings.TIME_ZONE

    now = adjust_datetime_to_timezone(
               datetime.now(),
               from_tz=os_timezone,
               to_tz=django_timezone)
    now = now.replace(tzinfo=None)
    return now


def localize_date(date, from_tz=None, to_tz=None):
    """
        Takes the given date/timezone
        and converts it to the sites date/timezone

        localize_date(date, from_tz, to_tz=None)
    """
    from timezones.utils import adjust_datetime_to_timezone

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
    currency_symbol = get_setting("site", "global", "currencysymbol")
    allow_commas = get_setting("site", "global", "allowdecimalcommas")

    if not currency_symbol:
        currency_symbol = "$"

    if not isinstance(mymoney, basestring):
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
        user.username = str(uuid.uuid1())[:7]
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

        from django.utils.html import strip_tags
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
                word = s.group(1)
                # remove the : from the word
                if word[-1] == ':':
                    word = word[:-1]

                one_words.append(word)
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
    if kwargs.has_key('path'):
        path = kwargs['path']
    else:
        path = getattr(settings,'PROJECT_ROOT','/var/log')

    if kwargs.has_key('filename'):
        filename = kwargs['filename']
    else:
        filename = 'filelog.txt'

    if kwargs.has_key('mode'):
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
    return ''.join(list(reversed(urlsafe_b64encode(password))))

def dec_pass(password):
    from base64 import urlsafe_b64decode

    pw_list = list(str(password))
    pw_list.reverse()

    return urlsafe_b64decode(''.join(pw_list))

def url_exists(url):
    import socket
    import httplib
    from parse_uri import ParseUri
    from django.contrib.sites.models import Site

    # parse url
    p = ParseUri()
    parsed_url = p.parse(url)

    # doesn't have a host so it's relative to the website
    if not parsed_url.host:
        parsed_url = p.parse(Site.objects.get_current().domain + url)

    conn = httplib.HTTPConnection(parsed_url.authority)
    conn.request("HEAD", parsed_url.path)

    try:
        socket.setdefaulttimeout(1.5)
        response = conn.getresponse()
        if response.status == 200:
            return True
    except:
        return False

def parse_image_sources(string):
    p = re.compile('<img[^>]* src=\"([^\"]*)\"[^>]*>')
    image_sources = re.findall(p, string)
    return image_sources

def make_image_object_from_url(image_url):
    import urllib2
    import socket
    from parse_uri import ParseUri
    from PIL import Image
    from StringIO import StringIO
    from django.contrib.sites.models import Site

    # parse url
    p = ParseUri()
    parsed_url = p.parse(image_url)

    # handle absolute and relative urls, Assuming http for now.
    if not parsed_url.host:
        parsed_url = p.parse(Site.objects.get_current().domain + image_url)
        parsed_url.protocol = "http"
        parsed_url.source = parsed_url.protocol + "://" + parsed_url.source

    request = urllib2.Request(parsed_url.source)
    request.add_header('User-Agent', settings.TENDENCI_USER_AGENT)
    opener = urllib2.build_opener()

    # make image object
    try:
        socket.setdefaulttimeout(1.5)
        data = opener.open(request).read() # get data
        im = Image.open(StringIO(data))
    except:
        im = None
    return im


def image_rescale(img, size, force=True):
    """Rescale the given image, optionally cropping it to make sure the result image has the specified width and height."""
    from PIL import Image as pil

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
    p = re.compile('{[#{%][^#}%]+[%}#]}', re.IGNORECASE)
    return p.search(string)


def get_template_list():
    """
    Get a list of files from the template
    directory that begin with 'default-'
    """
    file_list = []
    theme = get_setting('module', 'theme_editor', 'theme')
    if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
        theme_dir = settings.ORIGINAL_THEMES_DIR
    else:
        theme_dir = settings.THEMES_DIR

    current_dir = os.path.join(theme_dir, theme, template_directory)

    if os.path.isdir(current_dir):
        item_list = os.listdir(current_dir)
    else:
        item_list = []

    for item in item_list:
        current_item = os.path.join(current_dir, item)
        path_split = os.path.splitext(current_item)
        extension = path_split[1]
        base_name = os.path.basename(path_split[0])
        if os.path.isfile(current_item):
            if extension == ".html" and "default-" in base_name:
                base_display_name = base_name[8:].replace('-',' ').title()
                file_list.append((item,base_display_name,))
    return sorted(file_list)


def check_template(filename):
    """
    Check to see if the file exists in the theme root
    """
    current_file = os.path.join(settings.ORIGINAL_THEMES_DIR, THEME_ROOT, template_directory, filename)
    return os.path.isfile(current_file)

def template_exists(template):
    """
    Check if the template exists
    """
    try:
        get_template(template)
    except TemplateDoesNotExist:
        return False
    return True

def fieldify(s):
    """Convert the fields in the square brackets to the django field type.

        Example: "[First Name]: Lisa"
                    will be converted to
                "{{ first_name }}: Lisa"
    """
    #p = re.compile('(\[([\w\d\s_-]+)\])')
    p = re.compile('(\[(.*?)\])')
    return p.sub(slugify_fields, s)

def slugify_fields(match):
    return '{{ %s }}' % (slugify(match.group(2))).replace('-', '_')


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
        l = item.values()
    elif isinstance(item, list):
        l = item
    elif isinstance(item, basestring):
        l = list(item)

    # return not bool([i for i in l if i.strip)
    return not bool(''.join(l).strip())

    raise Exception


def normalize_newline(file_path):
    """
    Normalize the new lines for a file ```file_path```

    ```file_path``` is a relative path.
    """
    data = default_storage.open(file_path).read()
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
        page_range = range(1, max_num_in_group + 1)
        # middle group
        i = curr_page - int(max_num_in_group / 2)
        if i <= max_num_in_group:
            i = max_num_in_group
        else:
            page_range.extend(['...'])
        j = i + max_num_in_group
        if j > num_pages - max_num_in_group:
            j = num_pages - max_num_in_group
        page_range.extend(range(i, j))
        if j < num_pages - max_num_in_group:
            page_range.extend(['...'])
        # last group
        page_range.extend(range(num_pages - max_num_in_group,
                                num_pages + 1))
    else:
        page_range = range(1, num_pages + 1)
    return page_range


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
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
            print 'Salesforce authentication failed'

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
            if profile.company and contact.has_key('Company_Name__c'):
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
        modified_dt = default_storage.modified_time(file_path)
        if modified_dt + timedelta(days=ndays) < datetime.now():
            # the file is older than ndays, delete it
            default_storage.delete(file_path)
    for foldername in foldernames:
        folder_path = os.path.join(dir_path, foldername)
        directory_cleanup(folder_path, ndays)


def checklist_update(key):
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
    retstr = cStringIO.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    process_pdf(rsrcmgr, device, fp)
    device.close()
    mystr = retstr.getvalue()
    retstr.close()

    return mystr


def normalize_field_names(fieldnames):
    for i in range(0, len(fieldnames)):
        # clean up the fieldnames
        # ex: change First Name to first_name
        fieldnames[i] = fieldnames[i].lower().replace(' ', '_')

    return fieldnames
