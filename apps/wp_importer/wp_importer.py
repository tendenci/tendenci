import os
import urllib2
import time
import uuid
import sys
import re
from dateutil import parser
from datetime import datetime
from BeautifulSoup import BeautifulStoneSoup
from pages.models import Page
from articles.models import Article
from redirects.models import Redirect
from django.contrib.auth.models import User
from parse_uri import ParseUri

file_name = 'theofficialschipulblog.wordpress.2011-07-21.xml'
f = open(file_name, 'r')
xml = f.read()
f.close()

soup = BeautifulStoneSoup(xml)
items = soup.findAll('item')

user = User.objects.get(id=1)
uri_parser = ParseUri()


def replace_short_code(body):
    body = re.sub("(.*)(\\[caption.*caption=\")(.*)(\"\\])(.*)(<img.*(\"|/| )>)(.*)(\\[/caption\\])(.*)", "\\1\\6<div class=\"caption\">\\3</div>\\10", body)      
    return body

 # def remove_gallery(body):
 #     body = (.*)(\\[gallery.*)(\\.*\\])(.*)
 #     return body

def get_posts(items):
    post_list = []
    redirect_list = []
    for node in items:
        post_type = node.find('wp:post_type').string
        post_status = node.find('wp:status').string

        if post_type == 'post' and post_status == 'publish':
            title = unicode(node.find('title').contents[0])
            body = unicode(node.find('content:encoded').contents[0])
            body = replace_short_code(body)
            link = unicode(node.find('link').contents[0])
            slug = uri_parser.parse(link).path.strip('/')
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
    

def get_pages(items):
    page_list = []
    for node in items:
        post_type = node.find('wp:post_type').string
        post_status = node.find('wp:status').string

        if post_type == 'page' and post_status == 'publish':
            title = unicode(node.find('title').contents[0])
            body = unicode(node.find('content:encoded').contents[0])
            link = unicode(node.find('link').contents[0])
            slug = uri_parser.parse(link).path.strip('/')
           
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


def run():
    posts = get_posts(items)[0]
    for post in posts:
        a = Article(**post)
        a.save()
    redirects = get_posts(items)[1]
    for redir in redirects:
        r = Redirect(**redir)
        r.save()
    pages = get_pages(items)
    for page in pages:
        p = Page(**page)
        p.save()
  
run()