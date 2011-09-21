import datetime, encoder
from django.conf import settings
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from site_settings.utils import get_setting
from categories.models import Category
from pages.models import Page
from articles.models import Article
from news.models import News
from events.models import Event
from jobs.models import Job

def gen_xml():
    """
    Makes use of the encoder for xml to generate the wordpress export.
    """
    xml = encoder.XML()
    xml.write(
        '<rss version="2.0"\n' +
        '   xmlns:excerpt="http://wordpress.org/export/1.0/excerpt/"\n' +
        '   xmlns:content="http://purl.org/rss/1.0/modules/content/"\n' +
        '   xmlns:wfw="http://wellformedweb.org/CommentAPI/"\n' +
        '   xmlns:dc="http://purl.org/dc/elements/1.1/"\n' +
        '   xmlns:wp="http://wordpress.org/export/1.0/"\n' +
        '>'
    )
    xml.open("channel")
    encode_site(xml)
    encode_pages(xml)
    encode_articles(xml)
    encode_news(xml)
    encode_jobs(xml)
    encode_events(xml)
    xml.close("channel")
    xml.close("rss")
    return xml

def encode_site(xml):
    xml.open("title", depth=1)
    xml.write(get_setting('site', 'global', 'sitedisplayname'), depth=2)
    xml.close("title", depth=1)
    xml.open("description", depth=1)
    xml.close("description", depth=1)
    xml.open("pubDate", depth=1)
    xml.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), depth=2)
    xml.close("pubDate", depth=1)
    xml.open("language", depth=1)
    xml.write(get_setting('site', 'global', 'localizationlanguage'), depth=2)
    xml.close("language", depth=1)
    xml.open("wp:wxr_version", depth=1)
    xml.write(1.0, depth=2)
    xml.close("wp:wxr_version", depth=1)
    encode_categories(xml)
    
def encode_categories(xml):
    # since wordpress categories can only have single parents,
    # I will be not be associating the categories with any parents.
    ct_page = ContentType.objects.get_for_model(Page)
    ct_article = ContentType.objects.get_for_model(Article)
    ct_news = ContentType.objects.get_for_model(News)
    ct_job = ContentType.objects.get_for_model(Job)
    ct_event = ContentType.objects.get_for_model(Event)
    
    #encode tendenci categories
    cats = Category.objects.filter(
        Q(categoryitem_category__content_type=ct_page) or
        Q(categoryitem_category__content_type=ct_article) or
        Q(categoryitem_category__content_type=ct_news) or
        Q(categoryitem_category__content_type=ct_job) or
        Q(categoryitem_category__content_type=ct_event)).distinct()
    for cat in cats:
        xml.open("wp:category", depth=1)
        xml.open("wp:category_nicename", depth=2)
        xml.write(slugify(cat.name), depth=3)
        xml.close("wp:category_nicename", depth=2)
        xml.open("wp:category_parent", depth=2)
        xml.close("wp:category_parent", depth=2)
        xml.open("wp:cat_name", depth=2)
        xml.write("<![CDATA[%s]]>"%cat.name, depth=2)
        xml.close("wp:cat_name", depth=2)
        xml.close("wp:category", depth=1)
        
    #encode content types as categories
    types = ["article", "job", "event", "news", "page"]
    for type in types:
        xml.open("wp:category", depth=1)
        xml.open("wp:category_nicename", depth=2)
        xml.write(slugify(type), depth=3)
        xml.close("wp:category_nicename", depth=2)
        xml.open("wp:category_parent", depth=2)
        xml.close("wp:category_parent", depth=2)
        xml.open("wp:cat_name", depth=2)
        xml.write("<![CDATA[%s]]>"%type, depth=2)
        xml.close("wp:cat_name", depth=2)
        xml.close("wp:category", depth=1)

def encode_tags(xml):
    for tag in tags:
        xml.open("wp:tag", depth=1)
        xml.open("wp:tag_slug", depth=2)
        xml.write(slugify(tag), depth=3)
        xml.close("wp:tag_slug", depth=2)
        xml.open("wp:tag_name", depth=2)
        xml.write("<![CDATA[%s]]>"%tag, depth=3)
        xml.close("wp:tag_name", depth=2)
        xml.close("wp:tag", depth=1)

def encode_pages(xml):
    pages = Page.objects.filter(status=True)
    ct = ContentType.objects.get_for_model(Page)
    for page in pages:
        xml.open("item", depth=1)
        xml.open("title", depth=2)
        xml.write(page.title, depth=3)
        xml.close("title", depth=2)
        xml.open("pubDate", depth=2)
        xml.write(page.create_dt.strftime("%a, %d %b %Y %H:%M:%S %z"), depth=3)
        xml.close("pubDate", depth=2)
        xml.open("dc:creator", depth=2)
        xml.write("<![CDATA[%s]]>"%page.creator_username, depth=3)
        xml.close("dc:creator", depth=2)
        
        #get all the page's categories
        cats = Category.objects.filter(
            categoryitem_category__object_id = page.id,
            categoryitem_category__content_type = ct)
            
        for cat in cats:
            xml.open("category", depth=2)
            xml.write("<![CDATA[%s]]>"%cat.name, depth=3)
            xml.close("category", depth=2)
            xml.open("category", attrs={"domain":"category", "nicename":slugify(cat.name)}, depth=2)
            xml.write("<![CDATA[%s]]>"%cat.name, depth=3)
            xml.close("category", depth=2)
            
        #encode page as category
        xml.open("category", depth=2)
        xml.write("<![CDATA[page]]>", depth=3)
        xml.close("category", depth=2)
        xml.open("category", attrs={"domain":"category", "nicename":slugify("page")}, depth=2)
        xml.write("<![CDATA[page]]>", depth=3)
        xml.close("category", depth=2)
            
        xml.open("description", depth=2)
        xml.close("description", depth=2)
        xml.open("content:encoded", depth=2)
        xml.write("<![CDATA[%s]]>"%page.content, depth=3)
        xml.close("content:encoded", depth=2)
        xml.open("excerpt:encoded", depth=2)
        xml.write("<![CDATA[]]>", depth=3)
        xml.close("excerpt:encoded", depth=2)
        xml.open("wp:post_id", depth=2)
        xml.write(page.pk, depth=3)
        xml.close("wp:post_id", depth=2)
        xml.open("wp:post_date", depth=2)
        xml.write(page.create_dt, depth=3)
        xml.close("wp:post_date", depth=2)
        xml.open("wp:post_date_gmt", depth=2)
        xml.write(page.create_dt, depth=3)
        xml.close("wp:post_date_gmt", depth=2)
        xml.open("wp:comment_status", depth=2)
        xml.write("open", depth=3)
        xml.close("wp:comment_status", depth=2)
        xml.open("wp:ping_status", depth=2)
        xml.write("open", depth=3)
        xml.close("wp:ping_status", depth=2)
        xml.open("wp:post_name", depth=2)
        xml.write(slugify(page.title), depth=3)
        xml.close("wp:post_name", depth=2)
        xml.open("wp:status", depth=2)
        xml.write("publish", depth=3)
        xml.close("wp:status", depth=2)
        xml.open("wp:post_parent", depth=2)
        xml.write("0", depth=3)
        xml.close("wp:post_parent", depth=2)
        xml.open("wp:menu_order", depth=2)
        xml.write("0", depth=3)
        xml.close("wp:menu_order", depth=2)
        xml.open("wp:post_type", depth=2)
        xml.write("post", depth=3)
        xml.close("wp:post_type", depth=2)
        xml.open("wp:post_password", depth=2)
        xml.close("wp:post_password", depth=2)
        xml.open("wp:is_sticky", depth=2)
        xml.write(0, depth=3)
        xml.close("wp:is_sticky", depth=2)
        xml.close("item", depth=1)
        break

def encode_articles(xml):
    articles = Article.objects.filter(status=True)
    ct = ContentType.objects.get_for_model(Article)
    for article in articles:
        xml.open("item", depth=1)
        xml.open("title", depth=2)
        xml.write(article.headline, depth=3)
        xml.close("title", depth=2)
        xml.open("pubDate", depth=2)
        xml.write(article.create_dt.strftime("%a, %d %b %Y %H:%M:%S %z"), depth=3)
        xml.close("pubDate", depth=2)
        xml.open("dc:creator", depth=2)
        xml.write("<![CDATA[%s]]>"%article.creator_username, depth=3)
        xml.close("dc:creator", depth=2)
        
        #get all the article's categories
        cats = Category.objects.filter(
            categoryitem_category__object_id = article.id,
            categoryitem_category__content_type = ct)
            
        for cat in cats:
            xml.open("category", depth=2)
            xml.write("<![CDATA[%s]]>"%cat.name, depth=3)
            xml.close("category", depth=2)
            xml.open("category", attrs={"domain":"category", "nicename":slugify(cat.name)}, depth=2)
            xml.write("<![CDATA[%s]]>"%cat.name, depth=3)
            xml.close("category", depth=2)
            
        #encode article as category
        xml.open("category", depth=2)
        xml.write("<![CDATA[article]]>", depth=3)
        xml.close("category", depth=2)
        xml.open("category", attrs={"domain":"category", "nicename":slugify("article")}, depth=2)
        xml.write("<![CDATA[article]]>", depth=3)
        xml.close("category", depth=2)
            
        xml.open("description", depth=2)
        xml.close("description", depth=2)
        xml.open("content:encoded", depth=2)
        xml.write("<![CDATA[%s]]>"%article.body, depth=3)
        xml.close("content:encoded", depth=2)
        xml.open("excerpt:encoded", depth=2)
        xml.write("<![CDATA[]]>", depth=3)
        xml.close("excerpt:encoded", depth=2)
        xml.open("wp:post_id", depth=2)
        xml.write(article.pk, depth=3)
        xml.close("wp:post_id", depth=2)
        xml.open("wp:post_date", depth=2)
        xml.write(article.create_dt, depth=3)
        xml.close("wp:post_date", depth=2)
        xml.open("wp:post_date_gmt", depth=2)
        xml.write(article.create_dt, depth=3)
        xml.close("wp:post_date_gmt", depth=2)
        xml.open("wp:comment_status", depth=2)
        xml.write("open", depth=3)
        xml.close("wp:comment_status", depth=2)
        xml.open("wp:ping_status", depth=2)
        xml.write("open", depth=3)
        xml.close("wp:ping_status", depth=2)
        xml.open("wp:post_name", depth=2)
        xml.write(slugify(article.headline), depth=3)
        xml.close("wp:post_name", depth=2)
        xml.open("wp:status", depth=2)
        xml.write("publish", depth=3)
        xml.close("wp:status", depth=2)
        xml.open("wp:post_parent", depth=2)
        xml.write("0", depth=3)
        xml.close("wp:post_parent", depth=2)
        xml.open("wp:menu_order", depth=2)
        xml.write("0", depth=3)
        xml.close("wp:menu_order", depth=2)
        xml.open("wp:post_type", depth=2)
        xml.write("post", depth=3)
        xml.close("wp:post_type", depth=2)
        xml.open("wp:post_password", depth=2)
        xml.close("wp:post_password", depth=2)
        xml.open("wp:is_sticky", depth=2)
        xml.write(0, depth=3)
        xml.close("wp:is_sticky", depth=2)
        xml.close("item", depth=1)
        break
        
def encode_news(xml):
    newss = News.objects.filter(status=True)
    ct = ContentType.objects.get_for_model(News)
    for news in newss:
        xml.open("item", depth=1)
        xml.open("title", depth=2)
        xml.write(news.headline, depth=3)
        xml.close("title", depth=2)
        xml.open("pubDate", depth=2)
        xml.write(news.create_dt.strftime("%a, %d %b %Y %H:%M:%S %z"), depth=3)
        xml.close("pubDate", depth=2)
        xml.open("dc:creator", depth=2)
        xml.write("<![CDATA[%s]]>"%news.creator_username, depth=3)
        xml.close("dc:creator", depth=2)
        
        #get all the news's categories
        cats = Category.objects.filter(
            categoryitem_category__object_id = news.id,
            categoryitem_category__content_type = ct)
            
        for cat in cats:
            xml.open("category", depth=2)
            xml.write("<![CDATA[%s]]>"%cat.name, depth=3)
            xml.close("category", depth=2)
            xml.open("category", attrs={"domain":"category", "nicename":slugify(cat.name)}, depth=2)
            xml.write("<![CDATA[%s]]>"%cat.name, depth=3)
            xml.close("category", depth=2)
            
        #encode news as category
        xml.open("category", depth=2)
        xml.write("<![CDATA[news]]>", depth=3)
        xml.close("category", depth=2)
        xml.open("category", attrs={"domain":"category", "nicename":slugify("news")}, depth=2)
        xml.write("<![CDATA[news]]>", depth=3)
        xml.close("category", depth=2)
            
        xml.open("description", depth=2)
        xml.close("description", depth=2)
        xml.open("content:encoded", depth=2)
        xml.write("<![CDATA[%s]]>"%news.body, depth=3)
        xml.close("content:encoded", depth=2)
        xml.open("excerpt:encoded", depth=2)
        xml.write("<![CDATA[]]>", depth=3)
        xml.close("excerpt:encoded", depth=2)
        xml.open("wp:post_id", depth=2)
        xml.write(news.pk, depth=3)
        xml.close("wp:post_id", depth=2)
        xml.open("wp:post_date", depth=2)
        xml.write(news.create_dt, depth=3)
        xml.close("wp:post_date", depth=2)
        xml.open("wp:post_date_gmt", depth=2)
        xml.write(news.create_dt, depth=3)
        xml.close("wp:post_date_gmt", depth=2)
        xml.open("wp:comment_status", depth=2)
        xml.write("open", depth=3)
        xml.close("wp:comment_status", depth=2)
        xml.open("wp:ping_status", depth=2)
        xml.write("open", depth=3)
        xml.close("wp:ping_status", depth=2)
        xml.open("wp:post_name", depth=2)
        xml.write(slugify(news.headline), depth=3)
        xml.close("wp:post_name", depth=2)
        xml.open("wp:status", depth=2)
        xml.write("publish", depth=3)
        xml.close("wp:status", depth=2)
        xml.open("wp:post_parent", depth=2)
        xml.write("0", depth=3)
        xml.close("wp:post_parent", depth=2)
        xml.open("wp:menu_order", depth=2)
        xml.write("0", depth=3)
        xml.close("wp:menu_order", depth=2)
        xml.open("wp:post_type", depth=2)
        xml.write("post", depth=3)
        xml.close("wp:post_type", depth=2)
        xml.open("wp:post_password", depth=2)
        xml.close("wp:post_password", depth=2)
        xml.open("wp:is_sticky", depth=2)
        xml.write(0, depth=3)
        xml.close("wp:is_sticky", depth=2)
        xml.close("item", depth=1)
        break
        
def encode_jobs(xml):
    jobs = Job.objects.filter(status=True)
    ct = ContentType.objects.get_for_model(Job)
    for job in jobs:
        xml.open("item", depth=1)
        xml.open("title", depth=2)
        xml.write(job.title, depth=3)
        xml.close("title", depth=2)
        xml.open("pubDate", depth=2)
        xml.write(job.create_dt.strftime("%a, %d %b %Y %H:%M:%S %z"), depth=3)
        xml.close("pubDate", depth=2)
        xml.open("dc:creator", depth=2)
        xml.write("<![CDATA[%s]]>"%job.creator_username, depth=3)
        xml.close("dc:creator", depth=2)
        
        #get all the job's categories
        cats = Category.objects.filter(
            categoryitem_category__object_id = job.id,
            categoryitem_category__content_type = ct)
            
        for cat in cats:
            xml.open("category", depth=2)
            xml.write("<![CDATA[%s]]>"%cat.name, depth=3)
            xml.close("category", depth=2)
            xml.open("category", attrs={"domain":"category", "nicename":slugify(cat.name)}, depth=2)
            xml.write("<![CDATA[%s]]>"%cat.name, depth=3)
            xml.close("category", depth=2)
            
        #encode job as category
        xml.open("category", depth=2)
        xml.write("<![CDATA[job]]>", depth=3)
        xml.close("category", depth=2)
        xml.open("category", attrs={"domain":"category", "nicename":slugify("job")}, depth=2)
        xml.write("<![CDATA[job]]>", depth=3)
        xml.close("category", depth=2)
            
        xml.open("description", depth=2)
        xml.close("description", depth=2)
        xml.open("content:encoded", depth=2)
        xml.write("<![CDATA[%s]]>"%job.description, depth=3)
        xml.close("content:encoded", depth=2)
        xml.open("excerpt:encoded", depth=2)
        xml.write("<![CDATA[]]>", depth=3)
        xml.close("excerpt:encoded", depth=2)
        xml.open("wp:post_id", depth=2)
        xml.write(job.pk, depth=3)
        xml.close("wp:post_id", depth=2)
        xml.open("wp:post_date", depth=2)
        xml.write(job.create_dt, depth=3)
        xml.close("wp:post_date", depth=2)
        xml.open("wp:post_date_gmt", depth=2)
        xml.write(job.create_dt, depth=3)
        xml.close("wp:post_date_gmt", depth=2)
        xml.open("wp:comment_status", depth=2)
        xml.write("open", depth=3)
        xml.close("wp:comment_status", depth=2)
        xml.open("wp:ping_status", depth=2)
        xml.write("open", depth=3)
        xml.close("wp:ping_status", depth=2)
        xml.open("wp:post_name", depth=2)
        xml.write(slugify(job.title), depth=3)
        xml.close("wp:post_name", depth=2)
        xml.open("wp:status", depth=2)
        xml.write("publish", depth=3)
        xml.close("wp:status", depth=2)
        xml.open("wp:post_parent", depth=2)
        xml.write("0", depth=3)
        xml.close("wp:post_parent", depth=2)
        xml.open("wp:menu_order", depth=2)
        xml.write("0", depth=3)
        xml.close("wp:menu_order", depth=2)
        xml.open("wp:post_type", depth=2)
        xml.write("post", depth=3)
        xml.close("wp:post_type", depth=2)
        xml.open("wp:post_password", depth=2)
        xml.close("wp:post_password", depth=2)
        xml.open("wp:is_sticky", depth=2)
        xml.write(0, depth=3)
        xml.close("wp:is_sticky", depth=2)
        xml.close("item", depth=1)
        break
        
def encode_events(xml):
    events = Event.objects.filter(status=True)
    ct = ContentType.objects.get_for_model(Event)
    for event in events:
        xml.open("item", depth=1)
        xml.open("title", depth=2)
        xml.write(event.title, depth=3)
        xml.close("title", depth=2)
        xml.open("pubDate", depth=2)
        xml.write(event.create_dt.strftime("%a, %d %b %Y %H:%M:%S %z"), depth=3)
        xml.close("pubDate", depth=2)
        xml.open("dc:creator", depth=2)
        xml.write("<![CDATA[%s]]>"%event.creator_username, depth=3)
        xml.close("dc:creator", depth=2)
        
        #get all the event's categories
        cats = Category.objects.filter(
            categoryitem_category__object_id = event.id,
            categoryitem_category__content_type = ct)
            
        for cat in cats:
            xml.open("category", depth=2)
            xml.write("<![CDATA[%s]]>"%cat.name, depth=3)
            xml.close("category", depth=2)
            xml.open("category", attrs={"domain":"category", "nicename":slugify(cat.name)}, depth=2)
            xml.write("<![CDATA[%s]]>"%cat.name, depth=3)
            xml.close("category", depth=2)
            
        #encode event as category
        xml.open("category", depth=2)
        xml.write("<![CDATA[event]]>", depth=3)
        xml.close("category", depth=2)
        xml.open("category", attrs={"domain":"category", "nicename":slugify("event")}, depth=2)
        xml.write("<![CDATA[event]]>", depth=3)
        xml.close("category", depth=2)
            
        xml.open("description", depth=2)
        xml.close("description", depth=2)
        xml.open("content:encoded", depth=2)
        xml.write("<![CDATA[%s]]>"%event.description, depth=3)
        xml.close("content:encoded", depth=2)
        xml.open("excerpt:encoded", depth=2)
        xml.write("<![CDATA[]]>", depth=3)
        xml.close("excerpt:encoded", depth=2)
        xml.open("wp:post_id", depth=2)
        xml.write(event.pk, depth=3)
        xml.close("wp:post_id", depth=2)
        xml.open("wp:post_date", depth=2)
        xml.write(event.create_dt, depth=3)
        xml.close("wp:post_date", depth=2)
        xml.open("wp:post_date_gmt", depth=2)
        xml.write(event.create_dt, depth=3)
        xml.close("wp:post_date_gmt", depth=2)
        xml.open("wp:comment_status", depth=2)
        xml.write("open", depth=3)
        xml.close("wp:comment_status", depth=2)
        xml.open("wp:ping_status", depth=2)
        xml.write("open", depth=3)
        xml.close("wp:ping_status", depth=2)
        xml.open("wp:post_name", depth=2)
        xml.write(slugify(event.title), depth=3)
        xml.close("wp:post_name", depth=2)
        xml.open("wp:status", depth=2)
        xml.write("publish", depth=3)
        xml.close("wp:status", depth=2)
        xml.open("wp:post_parent", depth=2)
        xml.write("0", depth=3)
        xml.close("wp:post_parent", depth=2)
        xml.open("wp:menu_order", depth=2)
        xml.write("0", depth=3)
        xml.close("wp:menu_order", depth=2)
        xml.open("wp:post_type", depth=2)
        xml.write("post", depth=3)
        xml.close("wp:post_type", depth=2)
        xml.open("wp:post_password", depth=2)
        xml.close("wp:post_password", depth=2)
        xml.open("wp:is_sticky", depth=2)
        xml.write(0, depth=3)
        xml.close("wp:is_sticky", depth=2)
        xml.close("item", depth=1)
        break
