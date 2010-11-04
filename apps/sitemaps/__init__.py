# python 
from datetime import datetime
# django
from django.contrib.sitemaps import Sitemap
# local
from articles.models import Article
from news.models import News
from pages.models import Page
from photos.models import PhotoSet, Image
from stories.models import Story

class ArticleSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        
        sqs = Article.objects.search(release_dt__lte=datetime.now()).order_by('-create_dt')
        return [sq.object for sq in sqs]
                                        
    def lastmod(self, obj):
        return obj.create_dt
    
class NewsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        sqs = News.objects.search(release_dt__lte=datetime.now()).order_by('-create_dt')
        return [sq.object for sq in sqs]
                                        
    def lastmod(self, obj):
        return obj.create_dt

class PageSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.6
    
    def items(self):
        sqs = Page.objects.search().order_by('-update_dt')
        return [sq.object for sq in sqs]
    
    def lastmod(self, obj):
        return obj.update_dt

class PhotoSetSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    
    def items(self):
        sqs = PhotoSet.objects.search().order_by('-update_dt')
        return [sq.object for sq in sqs]
                                       
    def lastmod(self, obj):
        return obj.update_dt

class ImageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.3
    
    def items(self):
        sqs = Image.objects.search().order_by('-date_added')
        return [sq.object for sq in sqs]
                                        
    def lastmod(self, obj):
        return obj.date_added
#        
# Stories removed from sitemap because they are not end pieces of content.
# They are used in rotators and the end pages are not meant to be viewed. - JMO       
#
# class StorySitemap(Sitemap):
#     changefreq = "weekly"
#     priority = 0.2
#     
#     def items(self):
#         sqs = Story.objects.search().order_by('-create_dt')
#         return [sq.object for sq in sqs]
#                                         
#     def lastmod(self, obj):
#         return obj.create_dt