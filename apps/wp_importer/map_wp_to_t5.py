reesimport uuid
from BeautifulSoup import BeautifulStoneSoup
from pages.models import Page
from django.contrib.auth.models import User
from articles.models import Article
from parse_uri import ParseUri
from datetime import datetime
import os
import urllib2
import time

# I used ParseURI (written by Glen) to get the slug from the link in the given xml.

def run_wp_to_t5():
  file_name = 'theofficialschipulblog.wordpress.2011-07-21.xml'

  f = open(file_name, 'r')
  xml = f.read()
  f.close()

  pars = ParseUri()

  soup = BeautifulStoneSoup(xml)
  items = soup.findAll('item')
  posts_list = []
  pages_list = []

# grab posts and pages from xml
  for node in items:
      post_type = getattr(node.find('wp:post_type'), 'string', '')
      status = getattr(node.find('wp:status'), 'string', '')
      if post_type == 'post' and status == 'publish':
          title = unicode(node.find('title').contents[0])
          body = unicode(node.find('content:encoded').contents[0])
          post_date_content = unicode(node.find('wp:post_date').contents[0])
          post_date = datetime.strptime(post_date_content, '%Y-%m-%d %H:%M:%S')

          tags_list = getattr(node.find('category domain="post_tag"'), 'string', '')
          posts_list.append({
              'title': title,
              'creator': getattr(node.find('dc:creator'), 'string', ''),
              'post_type': post_type,
              'status': status,
              'guid': getattr(node.find('guid'), 'string', ''),
              'slug': getattr(node.find('link'), 'string', ''),
              'body': body,
              'post_date': post_date,
              'tags': tags_list
          })
      elif post_type == 'page' and status == 'publish':
          title = unicode(node.find('title').contents[0])
          body = unicode(node.find('content:encoded').contents[0])
          post_date_content = unicode(node.find('wp:post_date').contents[0])
          post_date = datetime.strptime(post_date_content, '%Y-%m-%d %H:%M:%S')
          pages_list.append({
              'title': title,
              'creator': getattr(node.find('dc:creator'), 'string', ''),
              'post_type': post_type,
              'status': status,
              'guid': getattr(node.find('guid'), 'string', ''),
              'slug': getattr(node.find('link'), 'string', ''),
              'post_date': post_date,
              'content': body
          })

# save posts and pages to database        
  user = User.objects.get(id=1)
  for item in posts_list:
      a = Article()
      slug = pars.parse(item['slug']).path.strip('/')
      a.guid = str(uuid.uuid1())
      a.slug = slug[:100]
      a.timezone = u'US/Central'
      a.body = item['body']
      a.headline = item['title']
      a.release_dt = item['post_date']
      a.tags = item['tags']
      a.syndicate = True
      a.featured = False
      a.allow_anonymous_view = True
      a.allow_user_view = False
      a.allow_member_view = False
      a.allow_anonymous_edit = False
      a.allow_user_edit = False
      a.allow_member_edit = False
      a.creator = user
      a.creator_username = user.username
      a.owner = user
      a.owner_username = user.username
      a.status = True
      a.status_detail = 'Active'
      a.save()

  for item in pages_list:
      p = Page()
      slug = pars.parse(item['slug']).path.strip('/')
      p.guid = str(uuid.uuid1())
      p.title = item['title']
      p.slug = slug[:100]
      p.content = item['content']
      p.view_contact_form = True
      p.syndicate = True
      p.allow_anonymous_view = True
      p.allow_user_view = False
      p.allow_member_view = False
      p.allow_anonymous_edit = False
      p.allow_user_edit = False
      p.allow_member_edit = False
      p.creator = user
      p.creator_username = user.username
      p.owner = user
      p.owner_username = user.username
      p.status = True
      p.status_detail = 'Active'
      p.save()

run_wp_to_t5()