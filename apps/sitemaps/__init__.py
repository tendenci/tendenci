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
    changefreq = "weekly"
    priority = 0.5
    
    def items(self):
        return Article.objects.filter(status=True, 
          release_dt__lte=datetime.now()).order_by('-create_dt')
                                        
    def lastmod(self, obj):
        return obj.create_dt
    
class NewsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    
    def items(self):
        return News.objects.filter(status=True,
           release_dt__lte=datetime.now()).order_by('-create_dt')
                                        
    def lastmod(self, obj):
        return obj.create_dt

class PageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    
    def items(self):
        return Page.objects.filter(status=True).order_by('-update_dt')
                                        
    def lastmod(self, obj):
        return obj.update_dt

class PhotoSetSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    
    def items(self):
        return PhotoSet.objects.filter(status=True).order_by('-update_dt')
                                        
    def lastmod(self, obj):
        return obj.update_dt

class ImageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    
    def items(self):
        return Image.objects.filter(status=True).order_by('-date_added')
                                        
    def lastmod(self, obj):
        return obj.date_added

class StorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    
    def items(self):
        return Story.objects.filter(status=True).order_by('-create_dt')
                                        
    def lastmod(self, obj):
        return obj.create_dt