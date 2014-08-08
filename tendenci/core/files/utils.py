from PIL import Image
from os.path import exists
from cStringIO import StringIO
import os
import httplib
import urllib
import urllib2
import socket
from urlparse import urlparse
from django.db import connection
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.shortcuts import Http404
from django.core.cache import cache as django_cache
from tendenci.core.base.utils import image_rescale
from tendenci.libs.boto_s3.utils import read_media_file_from_s3

from tendenci.core.files.models import File as TFile
from tendenci.core.files.models import file_directory
from tendenci.core.site_settings.utils import get_setting


def get_image(file, size, pre_key, crop=False, quality=90, cache=False, unique_key=None, constrain=False):
    """
    Gets resized-image-object from cache or rebuilds
    the resized-image-object using the original image-file.
    *pre_key is either:
        from tendenci.addons.photos.cache import PHOTO_PRE_KEY
        from tendenci.core.files.cache import FILE_IMAGE_PRE_KEY
    """

    size = validate_image_size(size)  # make sure it's not too big
    binary = None

    if cache:
        key = generate_image_cache_key(file, size, pre_key, crop, unique_key, quality, constrain)
        binary = django_cache.get(key)  # check if key exists

    if not binary:
        kwargs = {
            'crop': crop,
            'cache': cache,
            'quality': quality,
            'unique_key': unique_key,
            'constrain': constrain,
        }
        binary = build_image(file, size, pre_key, **kwargs)

    try:
        return Image.open(StringIO(binary))
    except:
        return ''


def build_image(file, size, pre_key, crop=False, quality=90, cache=False, unique_key=None, constrain=False):
    """
    Builds a resized image based off of the original image.
    """
    try:
        quality = int(quality)
    except TypeError:
        quality = 90

    if settings.USE_S3_STORAGE:
        content = read_media_file_from_s3(file)
        image = Image.open(StringIO(content))
    else:
        if hasattr(file, 'path') and exists(file.path):
            image = Image.open(file.path)  # get image
        else:
            raise Http404

    image_options = {'quality': quality}
    if image.format == 'GIF':
        image_options['transparency'] = 0

    format = image.format
    if image.format in ('GIF', 'PNG'):
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        image.format = format  # this is lost in conversion

    elif image.format == 'JPEG':
        # handle infamous error
        # IOError: cannot write mode P as JPEG
        if image.mode != "RGB":
            image = image.convert("RGB")

    if crop:
        image = image_rescale(image, size)  # thumbnail image
    else:
        format = image.format
        image = image.resize(size, Image.ANTIALIAS)  # resize image
        image.format = format

    binary = get_image_binary(image, **image_options)

    if cache:
        key = generate_image_cache_key(file, size, pre_key, crop, unique_key, quality, constrain)
        django_cache.add(key, binary, 60 * 60 * 24 * 30)  # cache for 30 days #issue/134

    return binary


def get_image_binary(image, **options):
    """
    Returns image binary
    """
    image.format = image.format or 'JPEG'

    output = StringIO()
    image.save(output, image.format, **options)
    binary = output.getvalue()
    output.close()

    return binary


def validate_image_size(size):
    """
    We cap our image sizes to avoid processor overload
    This method checks the size passed and returns
    a valid image size.
    """
    max_size = (2048, 2048)
    new_size = []

    # limit width and height exclusively
    for item in zip(size, max_size):
        if item[0] > item[1]:
            new_size.append(item[1])
        else:
            new_size.append(item[0])

    return tuple(new_size)


def aspect_ratio(image_size, new_size, constrain=False):
    """
    The image_size is a sequence of integers (200, 300)
    The new_size is a sequence of integers (200, 300)
    The constrain limits to within the new_size parameters.
    """
    orig_w, orig_h = image_size
    w, h = new_size

    # check if file size is 0, which means there's an exception
    if orig_w != 0 and orig_h != 0:
        if not constrain:
            if orig_w < w or orig_h < h:
                # prevent upscaling of images
                return orig_w, orig_h

    if not constrain and (w and h):
        return w, h

    if bool(w) != bool(h):
        if w:
            return constrain_size(image_size, [w, 0])
        return constrain_size(image_size, [0, h])

    if not constrain:
        if bool(w) != bool(h):
            return constrain_size(image_size, [w, 0])

    w1, h1 = constrain_size(image_size, [w, 0])
    w2, h2 = constrain_size(image_size, [0, h])

    if h1 == 0:
        h1 = w1
    if w1 == 0:
        w1 = h1
    if h2 == 0:
        h2 = w2
    if w2 == 0:
        w2 = h2

    if constrain:
        # check if h1,w1 breaks the boundaries of the constrain
        if h1 > h or w1 > w:
            # check for upscaling
            if orig_w < w2 or orig_h < h2:
                return orig_w, orig_h
            else:
                return w2, h2
        else:
            # check for upscaling
            if orig_w < w1 or orig_h < h1:
                return orig_w, orig_h
            else:
                return w1, h1

    if h1 <= h:
        return w1, h1

    return w2, h2


def constrain_size(image_size, new_size):
    """
    Take the biggest integer in the 2-item sequence
    and constrain on that integer.
    """

    w, h = new_size
    max_size = max(new_size)

    ow, oh = image_size  # original width and height
    if oh and ow:
        ow = float(ow)

        if w == max_size or h == '0':
            h = (oh / ow) * w
        else:  # height is max size
            w = h / (oh / ow)

    return int(w), int(h)


def generate_image_cache_key(file, size, pre_key, crop, unique_key, quality, constrain=False):
    """
    Generates image cache key. You can use this for adding,
    retrieving or removing a cache record.
    """
    str_size = ''
    if size:
        if 'x' in size:
            str_size = str(size)
        else:
            str_size = 'x'.join([str(i) for i in size])
    str_quality = str(quality)

    if crop:
        str_crop = "cropped"
    else:
        str_crop = ""

    if constrain:
        str_constrain = "constrain"
    else:
        str_constrain = ""

    # e.g. file_image.1294851570.200x300 file_image.<file-system-modified-time>.<width>x<height>
    if unique_key:
        key = '.'.join((settings.CACHE_PRE_KEY, pre_key, unique_key, str_size, str_crop, str_quality, str_constrain))
    else:
        key = '.'.join((settings.CACHE_PRE_KEY, pre_key, str(file.size), file.name, str_size, str_crop, str_quality, str_constrain))
    # Remove spaces so key is valid for memcached
    key = key.replace(" ", "_")

    return key


class AppRetrieveFiles(object):
    """
    Retrieve files (images) from src url.
    """
    def __init__(self, **kwargs):
        self.site_url = kwargs.get('site_url')
        self.site_domain = urllib2.Request(self.site_url).get_host()
        self.src_url = kwargs.get('src_url')
        self.src_domain = urllib2.Request(self.src_url).get_host()
        self.p = kwargs.get('p')
        self.replace_dict = {}
        self.total_count = 0
        self.broken_links = {}

    def process_app(self, app_name, **kwargs):
        if app_name == 'articles':
            from tendenci.addons.articles.models import Article

            articles = Article.objects.all()
            for article in articles:
                print 'Processing article - ', article.id,  article
                kwargs['instance'] = article
                kwargs['content_url'] = '%s%s' % (self.site_url,
                                                  article.get_absolute_url())
                updated, article.body = self.process_content(
                                        article.body, **kwargs)

                if updated:
                    article.save()
        elif app_name == 'news':
            from tendenci.addons.news.models import News
            news = News.objects.all()
            for n in news:
                print 'Processing news -', n.id, n
                kwargs['instance'] = n
                kwargs['content_url'] = '%s%s' % (self.site_url,
                                                  n.get_absolute_url())
                updated, n.body = self.process_content(
                                        n.body, **kwargs)
                if updated:
                    n.save()
        elif app_name == 'pages':
            from tendenci.apps.pages.models import Page
            pages = Page.objects.all()
            for page in pages:
                print 'Processing page -', page.id, page
                kwargs['instance'] = page
                kwargs['content_url'] = '%s%s' % (self.site_url,
                                                  page.get_absolute_url())
                updated, page.content = self.process_content(
                                        page.content, **kwargs)
                if updated:
                    page.save()
        elif app_name == 'jobs':
            from tendenci.addons.jobs.models import Job
            jobs = Job.objects.all()
            for job in jobs:
                print 'Processing job -', job.id, job
                kwargs['instance'] = job
                kwargs['content_url'] = '%s%s' % (self.site_url,
                                                  job.get_absolute_url())
                updated, job.description = self.process_content(
                                        job.description, **kwargs)
                if updated:
                    job.save()
        elif app_name == 'events':
            from tendenci.addons.events.models import Event, Speaker
            events = Event.objects.all()
            for event in events:
                print 'Processing event -', event.id, event
                kwargs['instance'] = event
                kwargs['content_url'] = '%s%s' % (self.site_url,
                                                  event.get_absolute_url())
                updated, event.description = self.process_content(
                                        event.description, **kwargs)
                if updated:
                    event.save()

            # speakers
            speakers = Speaker.objects.all()
            for speaker in speakers:
                print 'Processing event speaker -', speaker.id, speaker
                kwargs['instance'] = speaker
                [event] = speaker.event.all()[:1] or [None]
                if event:
                    kwargs['content_url'] = '%s%s' % (self.site_url,
                                                      event.get_absolute_url())
                else:
                    kwargs['content_url'] = 'event speaker %d' % speaker.id
                updated, speaker.description = self.process_content(
                                        speaker.description, **kwargs)
                if updated:
                    speaker.save()

        elif app_name == 'files':
            # we need to dig the info from mig_files_file_t4_to_t5
            cursor = connection.cursor()
            mig_file_table = 'mig_files_file_t4_to_t5'
            cursor.execute("""select count(*) from pg_class
                            where relname='%s' and relkind='r'
                            """ % mig_file_table)
            row = cursor.fetchone()
            if row[0] == 0:
                print 'File migration table %s does not exist. Exiting..' % mig_file_table
                return
            tfiles = TFile.objects.all()
            for tfile in tfiles:
                kwargs['content_url'] = '%s%s' % (self.site_url,
                                                  tfile.get_absolute_url())
                self.check_file(tfile, cursor, mig_file_table, **kwargs)

        print "\nTotal links updated for %s: " % app_name, self.total_count

    def process_content(self, content, **kwargs):
        self.replace_dict = {}

        matches = self.p.findall(content)
        print '... ', len(matches), 'matches found.'

        for match in matches:
            link = match[1]
            self.process_link(link, **kwargs)

        # find and replace urls
        if self.replace_dict:
            updated = True
            for url_find, url_repl in self.replace_dict.iteritems():
                content = content.replace(url_find, url_repl)
            count = self.replace_dict.__len__()
            print '...', count, 'link(s) replaced.'
            self.total_count += count
        else:
            updated = False

        return updated, content

    def check_file(self, tfile, cursor, mig_file_table, **kwargs):
        """
        Check and download files from t4 based on the info in the
        table mig_files_file_t4_to_t5
        """
        if tfile.file:
            file_path = tfile.file.name
            # if file doesn't exist
            if not default_storage.exists(file_path):
                # get t4 url from the mig table
                file_name = os.path.basename(file_path)
                sql = """select t4_object_id, t4_object_type
                        from %s
                        where t5_id=%d
                     """ % (mig_file_table, tfile.id)
                cursor.execute(sql)
                row = cursor.fetchone()
                if row:
                    (t4_object_id, t4_object_type) = row
                    t4_relative_url = '/attachments/%s/%s/%s' % (
                                t4_object_type,
                                t4_object_id,
                                file_name)
                    t4_url = '%s%s' % (self.src_url, t4_relative_url)
                    # if link exists on the t4 site, go get it
                    if self.link_exists(t4_relative_url, self.src_domain):
                        tfile.file.save(file_path,
                                        ContentFile(
                                    urllib2.urlopen(t4_url).read()))
                        print tfile.get_absolute_url(), 'file downloaded.'
                    else:
                        # t4_url not exist
                        self.add_broken_link(t4_url, **kwargs)
                else:
                    # cannot retrieve the info from the mig table
                    self.add_broken_link('No entry in mig table', **kwargs)

    def process_link(self, link, **kwargs):
        # check if this is a broken link
        # the link can from three different sources:
        # this site:
        #    absolute url
        #    relative url
        # the src site:
        #    absolute url
        # the other sites:
        #    absolute url

        # handle absolute url
        cleaned_link = link.replace('&amp;', '&')
        o = urlparse(cleaned_link)
        relative_url = urllib.quote(urllib.unquote(o.path))
        hostname = o.hostname

        # skip if link is external other than the src site.
        if hostname and hostname not in (self.site_domain,
                                         self.site_domain.lstrip('www.'),
                                         self.src_domain,
                                         self.src_domain.lstrip('www.')):
            if not self.link_exists(relative_url, hostname):
                print '-- External broken link: ', link
                self.add_broken_link(link, **kwargs)
            return

        # if link doesn't exist on the site but on the src
        if not self.link_exists(relative_url, self.site_domain):
            if self.link_exists(relative_url, self.src_domain):
                url = '%s%s' % (self.src_url, relative_url)
                # go get from the src site
                tfile = self.save_file_from_url(url, kwargs.get('instance'))
                self.replace_dict[link] = tfile.get_absolute_url()
            else:
                print '** Broken link - ', link, "doesn't exist on both sites."
                self.add_broken_link(link, **kwargs)

    def link_exists(self, relative_link, domain):
        """
        Check if this link exists for the given domain.

        example of a relative_link:
        /images/newsletter/young.gif
        """
        conn = httplib.HTTPConnection(domain)
        try:
            conn.request('HEAD', relative_link)
            res = conn.getresponse()
            conn.close()
        except socket.gaierror:
            return False

        return res.status in (200, 304)

    def add_broken_link(self, broken_link, **kwargs):
        """
        Append the broken link to the list.
        """
        key = kwargs['content_url']
        if not key in self.broken_links.keys():
            self.broken_links[key] = [broken_link]
        else:
            self.broken_links[key].append(broken_link)

    def save_file_from_url(self, url, instance):
        file_name = os.path.basename(urllib.unquote(url).replace(' ', '_'))
        tfile = TFile()
        tfile.name = file_name
        tfile.content_type = ContentType.objects.get_for_model(instance)
        tfile.object_id = instance.id
        if hasattr(instance, 'creator'):
            tfile.creator = instance.creator
        if hasattr(instance, 'creator_username'):
            tfile.creator_username = instance.creator_username
        if hasattr(instance, 'owner'):
            tfile.owner = instance.owner
        if hasattr(instance, 'owner_username'):
            tfile.owner_username = instance.owner_username

        #file_path = file_directory(tfile, tfile.name)
        tfile.file.save(file_name, ContentFile(urllib2.urlopen(url).read()))
        tfile.save()
        return tfile


def get_max_file_upload_size(file_module=False):
    global_max_upload_size = (get_setting('site', 'global', 'maxfilesize') or 
                              "26214400")  # default value if ever site setting is missing
    if file_module:
        return int(get_setting('module', 'files', 'maxfilesize') or global_max_upload_size)
    return int(global_max_upload_size)
