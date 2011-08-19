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

from pages.models import Page
from articles.models import Article
from redirects.models import Redirect
from files.models import File

from django.contrib.auth.models import User
from django.conf import settings
from django.template import RequestContext

# Replaces shortcodes in the body of an article with appropriate HTML structures.
  
def replace_short_code(body):

    body = re.sub("(.*)(\\[caption.*caption=\")(.*)(\"\\])(.*)(<img.*(\"|/| )>)(.*)(\\[/caption\\])(.*)", "\\1\\6<div class=\"caption\">\\3</div>\\10", body)      
    body = re.sub("(.*)(\\[gallery?.*?\\])(.*)", '', body)
    return body

def get_posts(items, uri_parser, user):
    """
    Find each item marked "post" in items
    If that Article has already been created, skip it.
    If not, create Article object and Redirect object.
    """
    post_list = []
    redirect_list = []
    alreadyThere = False
    for node in items:
        post_type = node.find('wp:post_type').string
        post_status = node.find('wp:status').string

        if post_type == 'post' and post_status == 'publish':
            link = unicode(node.find('link').contents[0])
            slug = uri_parser.parse(link).path.strip('/')

            for post in Article.objects.all():
                if post.slug == slug[:100]:
                    alreadyThere = True
                    break
                else:
                    alreadyThere = False
            
            if not alreadyThere:
                title = unicode(node.find('title').contents[0])
                body = unicode(node.find('content:encoded').contents[0])
                body = replace_short_code(body)
                body = correct_media_file_path(body, uri_parser)
                post_date = unicode(node.find('wp:post_date').contents[0])
                post_dt = datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
                
                tags_raw = node.findAll('category', domain="post_tag")
                tags_list = []
            
                if tags_raw:
                    for tag in tags_raw:
                        if len(','.join(tags_list)) + len(tag.string) <= 255:
                            tags_list.append(tag.string[:50])

            
                post_list.append({
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
                    'allow_anonymous_edit': False,
                    'allow_user_edit': False,
                    'allow_member_edit': False,
                    'owner': user,
                    'owner_username': user.username,
                    'status': True,
                    'status_detail': 'active'
                })

                redirect_list.append({
                    'from_url': slug[:100],
                    'to_url': os.path.join('articles', slug[:100])
                })

    return post_list, redirect_list

# Find each item marked "page" in items.If that Page has already been created, do nothing. If not, create Page object.
    
def get_pages(items, uri_parser, user):
 
    page_list = []
    alreadyThere = False

    for node in items:
        post_type = node.find('wp:post_type').string
        post_status = node.find('wp:status').string

        if post_type == 'page' and post_status == 'publish':
            link = unicode(node.find('link').contents[0])
            slug = uri_parser.parse(link).path.strip('/')

            for page in Page.objects.all():
                if page.slug == slug[:100]:
                    alreadyThere = True
                    break
                else:
                    alreadyThere = False
           
            if not alreadyThere:
                title = unicode(node.find('title').contents[0])
                body = unicode(node.find('content:encoded').contents[0])
                body = correct_media_file_path(body, uri_parser)
                page_list.append({
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
                    'allow_anonymous_edit': False,
                    'allow_user_edit': False,
                    'allow_member_edit': False,
                    'owner': user,
                    'owner_username': user.username,
                    'status': True,
                    'status_detail': 'active'
                })

    return page_list

#   Find any URL contained in an "attachment" If that File has already been created, skip it. If not, go to the URL, and save the media there as a File.
  
def get_media(items, uri_parser, user):
    
    for node in items:
        post_type = node.find('wp:post_type').string
        if post_type == 'attachment':
            media_url_in_attachment = node.find('wp:attachment_url').string
            media_url = uri_parser.parse(media_url_in_attachment).file
            media_url = os.path.join(settings.MEDIA_ROOT, media_url)

            alreadyThere = False

            for media_path in File.objects.all():
                if media_url == media_path.file:
                    alreadyThere = True
                    break
            
            if not alreadyThere:
                source = urllib2.urlopen(media_url_in_attachment).read()

                with open(media_url, 'wb') as f:
                    f.write(source)
                    file_path = f.name

                new_media = File(guid=unicode(uuid.uuid1()), file=file_path, creator=user, owner=user)
                new_media.save()

# For each File in the database, replace an instance of that file's URL in the given HTML with a file path.
    
def correct_media_file_path(body, uri_parser):
    
    for overwrite in File.objects.all():
        print 'Got to the for loop'
        print overwrite.basename() + '\n'
        match = re.search("(.*)(http://.*\\/?\\/\\b\\w+\\/)((\\S+)(\\-\\d+x.*?\\S*.*)|(\\S+.*?\\S+))(\\.\\S+)(\\\".*)", body)
        if match:
            match.group()
            if overwrite.basename() == match.group(3) + match.group(7):
                print 'I am in the if statement before sub'
                print overwrite.basename() + '\n'
                #media_overwrite.endswith(match.group(3)+match.group(7)):
                #body = re.sub("(.*)(http://.*\\/?\\/\\b\\w+\\/)(" + re.escape(overwrite.basename())")(\\.\\S+)(\\\".*)", "\\1/files/" + match.group(3) + "/\\7", body)
                body = re.sub("(.*)(http://.*\\/?\\/\\b\\w+\\/)(" + re.escape(overwrite.basename()) + ".*?)(\\\".*)", "\\1/files/" + str(overwrite.pk) + "/\\4", body)
                print 'I am after re.sub'
                print overwrite.basename() + '\n'

            elif overwrite.basename() == match.group(3) + match.group(7):
                print 'In the elif before re.sub'
                body = re.sub("(.*)(http://.*\\/?\\/\\b\\w+\\/)("+ re.escape(match.group(6)) +")(\\.\\S+)(\\\".*)", "\\1/files/" + str(overwrite.pk) + "/\\7", body)
                print 'In elif after re.sub'
    return body
    print 'After return'

# Parse the given xml file using BeautifulSoup. Save all Article, Redirect and Page objects.

def run(file_name, request):
    
    f = open(file_name, 'r')
    xml = f.read()
    f.close()
    os.remove(file_name)

    uri_parser = ParseUri()
    soup = BeautifulStoneSoup(xml)
    items = soup.findAll('item')

    user = request.user

    get_media(items, uri_parser, user)
    posts = get_posts(items, uri_parser, user)[0]
    for post in posts:
        a = Article(**post)
        a.save()
    redirects = get_posts(items, uri_parser, user)[1]
    for redir in redirects:
        r = Redirect(**redir)
        r.save()
    pages = get_pages(items, uri_parser, user)
    for page in pages:
        p = Page(**page)
        p.save()