import os
import re
# python
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.template.defaultfilters import slugify
from site_settings.utils import get_setting
from theme.utils import get_theme_root

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

def now_localized():
    from datetime import datetime
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
    import locale
    locale.setlocale(locale.LC_ALL, '')
    currency_symbol = get_setting("site", "global", "currencysymbol")
   
    if not currency_symbol: currency_symbol = "$"

    if not isinstance(mymoney, str):
        if mymoney >= 0:
            return currency_symbol + locale.format('%.2f', mymoney, True)
        else:
            return currency_symbol + '(%s)' % (locale.format('%.2f', abs(mymoney), True))
    else:
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
        from notification import models as notification
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
    import re
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
    import Image as pil
    
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
    
    return img

def in_group(user, group):
    """
        Tells you if a user is in a particular group
        in_group(user,'administrator')
        returns boolean
    """
    return group in [dict['name'].lower() for dict in user.groups.values('name')]

def detect_template_tags(string):
    """
        Used to detect wether or not any string contains
        template tags in the system
        returns boolean
    """
    import re
    p = re.compile('{[#{%][^#}%]+[%}#]}', re.IGNORECASE)
    return p.search(string)

def get_template_list():
    """
    Get a list of files from the template
    directory that begin with 'default-'
    """
    file_list = []
    current_dir = os.path.join(THEME_ROOT, template_directory)
    if os.path.isdir(current_dir):
        item_list = os.listdir(current_dir)
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
    return file_list
    
def check_template(filename):
    """
    Check to see if the file exists
    """
    current_file = os.path.join(THEME_ROOT, template_directory, filename)
    return os.path.isfile(current_file)

def fieldify(str):
    """Convert the fields in the square brackets to the django field type. 
    
        Example: "[First Name]: Lisa" 
                    will be converted to 
                "{{ first_name }}: Lisa"
    """
    #p = re.compile('(\[([\w\d\s_-]+)\])')
    p = re.compile('(\[(.*?)\])')
    return p.sub(slugify_fields, str)

def slugify_fields(match):
    return '{{ %s }}' % (slugify(match.group(2))).replace('-', '_')
