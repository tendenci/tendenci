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

def gen_xml():
    """
    Makes use of the encoder for xml to generate the wordpress export.
    """
    xml = encoder.XML()
    xml.open("rss", attrs={
        "version":"2.0",
        "xmlns:excerpt":"http://wordpress.org/export/1.0/excerpt/",
        "xmlns:content":"http://purl.org/rss/1.0/modules/content/",
        "xmlns:wfw":"http://wellformedweb.org/CommentAPI/",
        "xmlns:dc":"http://purl.org/dc/elements/1.1/",
        "xmlns:wp":"http://wordpress.org/export/1.0/"})
    xml.open("channel")
    encode_site(xml)
    encode_pages(xml)
    xml.close("channel")
    xml.close("rss")
    return xml

def encode_site(xml):
    xml.open("title")
    xml.write(get_setting('site', 'global', 'sitedisplayname'))
    xml.close("title")
    xml.open("link")
    xml.write(get_setting('site', 'global', 'siteurl'))
    xml.close("link")
    xml.open("description")
    xml.close("description")
    xml.open("pubDate")
    xml.write(str(datetime.datetime.now()))
    xml.close("pubDate")
    xml.open("generator")
    xml.write(get_setting('site', 'global', 'siteurl'))
    xml.close("generator")
    xml.open("language")
    xml.write(get_setting('site', 'global', 'localizationlanguage'))
    xml.close("language")
    xml.open("wp:wxr_version")
    xml.write(1.0)
    xml.close("wp:wxr_version")
    xml.open("wp:base_site_url")
    xml.write(get_setting('site', 'global', 'siteurl'))
    xml.close("wp:base_site_url")
    xml.open("wp:base_blog_url")
    xml.write(get_setting('site', 'global', 'siteurl'))
    xml.close("wp:base_blog_url")
    encode_categories(xml)
    xml.open("generator")
    xml.write(get_setting('site', 'global', 'siteurl'))
    xml.close("generator")
    xml.open("cloud", attrs={
        "domain":str(get_setting('site', 'global', 'siteurl')),
        "port":'80',
        "path":'/?rsscloud=notify',
        "registerProcedure":'', 
        "protocol":'http-post'})
    
def encode_categories(xml):
    # since wordpress categories can only have single parents,
    # I will be not be associating the categories with any parents.
    ct_page = ContentType.objects.get_for_model(Page)
    ct_article = ContentType.objects.get_for_model(Article)
    ct_news = ContentType.objects.get_for_model(News)
    ct_event = ContentType.objects.get_for_model(Event)
    cats = Category.objects.filter(
        Q(categoryitem_category__content_type=ct_page) or
        Q(categoryitem_category__content_type=ct_article) or
        Q(categoryitem_category__content_type=ct_news) or
        Q(categoryitem_category__content_type=ct_event)).distinct()
    for cat in cats:
        xml.open("wp:category")
        xml.open("wp:category_nicename")
        xml.write(slugify(cat.name))
        xml.close("wp:category_nicename")
        xml.open("wp:category_parent")
        xml.close("wp:category_parent")
        xml.open("wp:cat_name")
        xml.write("<![CDATA[%s]]>"%cat.name)
        xml.close("wp:cat_name")
        xml.close("wp:category")

def encode_tags(xml):
    for tag in tags:
        xml.open("wp:tag")
        xml.open("wp:tag_slug")
        xml.write(slugify(tag))
        xml.close("wp:tag_slug")
        xml.open("wp:tag_name")
        xml.write("<![CDATA[%s]]>"%tag)
        xml.close("wp:tag_name")
        xml.close("wp:tag")

def encode_pages(xml):
    pages = Page.objects.all()
    ct = ContentType.objects.get_for_model(Page)
    for page in pages:
        xml.open("item")
        xml.open("title")
        xml.write("Hello world!")
        xml.close("title")
        xml.open("link")
        xml.write(page.get_absolute_url())
        xml.close("link")
        xml.open("pubDate")
        xml.write(str(page.create_dt))
        xml.close("pubDate")
        xml.open("dc:creator")
        xml.write("<![CDATA[%s]]>"%page.creator_username)
        xml.close("dc:creator")
        
        #get all the page's categories
        cats = Category.objects.filter(
            categoryitem_category__object_id = page.id,
            categoryitem_category__content_type = ct)
            
        for cat in cats:
            xml.open("category")
            xml.write("<![CDATA[%s]]>"%cat.name)
            xml.close("category")
            xml.open("category", attrs={"domain":"category", "nicename":slugify(cat.name)})
            xml.write("<![CDATA[%s]]>"%cat.name)
            xml.close("category")

        xml.open("guid", attrs={"isPermaLink":"false"})
        xml.write(page.get_absolute_url())
        xml.close("guid")
        xml.open("description")
        xml.close("description")
        xml.open("content:encoded")
        xml.write("<![CDATA[%s]]>"%page.content)
        xml.close("content:encoded")
        xml.open("excerpt:encoded")
        xml.write("<![CDATA[]]>")
        xml.close("excerpt:encoded")
        xml.open("wp:post_id")
        xml.write(page.pk)
        xml.close("wp:post_id")
        xml.open("wp:post_date")
        xml.write(page.create_dt)
        xml.close("wp:post_date")
        xml.open("wp:post_date_gmt")
        xml.write(page.create_dt)
        xml.close("wp:post_date_gmt")
        xml.open("wp:comment_status")
        xml.write("open")
        xml.close("wp:comment_status")
        xml.open("wp:ping_status")
        xml.write("open")
        xml.close("wp:ping_status")
        xml.open("wp:post_name")
        xml.write(slugify(page.title))
        xml.close("wp:post_name")
        xml.open("wp:status")
        xml.write("publish")
        xml.close("wp:status")
        xml.open("wp:post_parent")
        xml.write("0")
        xml.close("wp:post_parent")
        xml.open("wp:menu_order")
        xml.write("0")
        xml.close("wp:menu_order")
        xml.open("wp:post_type")
        xml.write("post")
        xml.close("wp:post_type")
        xml.open("wp:post_password")
        xml.close("wp:post_password")
        xml.open("wp:is_sticky")
        xml.write(0)
        xml.close("wp:is_sticky")
        xml.open("wp:postmeta")
        xml.open("wp:meta_key")
        xml.write("_edit_lock")
        xml.close("wp:meta_key")
        xml.open("wp:meta_value")
        xml.write("<![CDATA[1316100692:20597443]]>")
        xml.close("wp:meta_value")
        xml.close("wp:postmeta")
        xml.open("wp:postmeta")
        xml.open("wp:meta_key")
        xml.write("_edit_last")
        xml.close("wp:meta_key")
        xml.open("wp:meta_value")
        xml.write("<![CDATA[20597443]]>")
        xml.close("wp:meta_value")
        xml.close("wp:postmeta")
        xml.open("wp:postmeta")
        xml.open("wp:meta_key")
        xml.write("jabber_published")
        xml.close("wp:meta_key")
        xml.open("wp:meta_value")
        xml.write("<![CDATA[1316008223]]>")
        xml.close("wp:meta_value")
        xml.close("wp:postmeta")
        xml.close("item")
        break
        
