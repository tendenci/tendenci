import os
import urllib2
import time
import uuid
import sys
import re

from dateutil import parser
from datetime import datetime
from BeautifulSoup import BeautifulStoneSoup
from parse_uri import ParseUri

from tendenci.apps.pages.models import Page
from tendenci.addons.articles.models import Article
from tendenci.apps.redirects.models import Redirect
from tendenci.core.files.models import File
from tendenci.apps.wp_importer.models import AssociatedFile

from django.contrib.auth.models import User
from django.conf import settings
from django.template import RequestContext

def replace_short_code(body):
    """
    Replaces shortcodes in the body of an article with appropriate HTML structures.
    """
    # remove CDATA elements
    body = re.sub("^<!\\[CDATA\\[", "", body)
    body = re.sub("\\]\\]>$", "", body)

    body = re.sub("(.*)(\\[caption.*caption=\")(.*)(\"\\])(.*)(<img.*(\"|/| )>)(.*)(\\[/caption\\])(.*)", "\\1\\6<div class=\"caption\">\\3</div>\\10", body)
    body = re.sub("(.*)(\\[gallery?.*?\\])(.*)", '', body)
    return body

def get_posts(item, uri_parser, user):
    """
    If the given Article has already been created, skip it.
    If not, create Article object and Redirect object.
    """
    alreadyThere = False

    if item.find('link'):
        link = unicode(item.find('link').contents[0])
        slug = uri_parser.parse(link).path.strip('/')
    else:
        # if no slug, grab the post id
        slug = unicode(item.find('wp:post_id').contents[0])

    for article in Article.objects.all():
        if article.slug == slug[:100]:
            alreadyThere = True
            break

    if not alreadyThere:
        title = unicode(item.find('title').contents[0])
        post_id = item.find('wp:post_id').string
        post_id = int(post_id)
        body = unicode(item.find('content:encoded').contents[0])
        body = replace_short_code(body)

        try:
            # There may not be a file associated with a post.
            # If so, catch that error.
            fgroup = AssociatedFile.objects.filter(post_id=post_id)
            for f in fgroup:
                body = correct_media_file_path(body, f.file)

        except:
            pass

        post_date = unicode(item.find('wp:post_date').contents[0])
        #post_dt = datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
        post_dt = post_date

        tags_raw = item.findAll('category', domain="post_tag")
        tags_list = []

        if tags_raw:
            for tag in tags_raw:
                if len(','.join(tags_list)) + len(tag.string) <= 255:
                    tags_list.append(tag.string[:50])

        article = {
            'headline': title,
            'guid': str(uuid.uuid1()),
            'slug': slug[:100],
            'body': body,
            'tags': ','.join(tags_list),
            'timezone': 'US/Central',
            'syndicate': True,
            'featured': False,
            'release_dt': post_dt,
            'creator': user,
            'creator_username': user.username,
            'allow_anonymous_view': True,
            'allow_user_view': False,
            'allow_member_view': False,
            'allow_user_edit': False,
            'allow_member_edit': False,
            'owner': user,
            'owner_username': user.username,
            'status': True,
            'status_detail': 'active'
        }

        redirect = {
            'from_url': slug[:100],
            'to_url': os.path.join('articles', slug[:100])
        }

        a = Article(**article)
        a.save()
        r = Redirect(**redirect)
        r.save()

def get_pages(item, uri_parser, user):
    """
    Find each item marked "page" in items.
    If that Page has already been created, do nothing.
    If not, create Page object.
    """
    alreadyThere = False
    link = unicode(item.find('link').contents[0])
    slug = uri_parser.parse(link).path.strip('/')

    for page in Page.objects.all():
        if page.slug == slug[:100]:
            alreadyThere = True
            break

    if not alreadyThere:
        title = unicode(item.find('title').contents[0])
        post_id = item.find('wp:post_id').string
        post_id = int(post_id)
        body = unicode(item.find('content:encoded').contents[0])
        body = replace_short_code(body)
        try:
            fgroup = AssociatedFile.objects.filter(post_id=post_id)
            for f in fgroup:
                body = correct_media_file_path(body, f.file)

        except:
            pass

        page = {
            'title': title,
            'guid': str(uuid.uuid1()),
            'slug': slug[:100],
            'content': body,
            #'timezone': 'US/Central',
            'syndicate': True,
            #'featured': False,
            #'create_dt': datetime.now(),
            'creator': user,
            'creator_username': user.username,
            'allow_anonymous_view': True,
            'allow_user_view': False,
            'allow_member_view': False,
            'allow_user_edit': False,
            'allow_member_edit': False,
            'owner': user,
            'owner_username': user.username,
            'status': True,
            'status_detail': 'active'
        }

        p = Page(**page)
        p.save()

def get_media(item, uri_parser, user):
    """
    Find any URL contained in an "attachment."
    If that File has already been created, skip it.
    If not, go to the URL, and save the media there as a File.
    Loop through Articles and Pages and replace links.
    """
    media_url_in_attachment = item.find('wp:attachment_url').string
    media_url = uri_parser.parse(media_url_in_attachment).file
    media_url = os.path.join(settings.MEDIA_ROOT, media_url)

    post_id = item.find('wp:post_parent').string
    post_id = int(post_id)

    alreadyThere = False

    for url in File.objects.all():
        if media_url == url.file:
            alreadyThere = True
            # This assignment will make sure the file gets replaced in the HTML even if
            # it's an old file that already exists in the database.
            new_media = url
            break

    if not alreadyThere:
        source = urllib2.urlopen(media_url_in_attachment).read()

        with open(media_url, 'wb') as f:
            f.write(source)
            file_path = f.name

        new_media = File(guid=unicode(uuid.uuid1()), file=file_path, creator=user, owner=user)
        new_media.save()

    temporary = AssociatedFile(post_id=post_id, file=new_media)
    temporary.save()


def correct_media_file_path(body, file):
    """
    Replace an instance of the given file's URL in the given HTML with a file path.
    """
    match = re.search("(.*)(http://.*\\/?\\/\\b\\w+\\/)((\\S+)(\\-\\d+x.*?\\S*.*)|(\\S+.*?\\S+))(\\.\\S+)(\\\".*)", body)
    if match:
        match.group()

        if match.group(4) == None and file.basename() == match.group(6) + match.group(7):
            # if the file is unsized
            body = re.sub("(.*)(http://.*\\/?\\/\\b\\w+\\/)(" + re.escape(file.basename()) + ".*?)(\\\".*)", "\\1/files/" + str(file.pk) + "/\\4", body)
        elif match.group(6) == None and file.basename() == match.group(4) + match.group(7):
            # if the file is sized
            body = re.sub("(.*)(http://.*\\/?\\/\\b\\S+\\/)(" + re.escape(match.group(4) + match.group(5) + match.group(7)) + ".*?)(\\\".*)", "\\1/files/" + str(file.pk) + "/\\4", body)

    return body

