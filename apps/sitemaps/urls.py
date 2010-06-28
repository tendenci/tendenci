from django.conf.urls.defaults import patterns
from sitemaps import ArticleSitemap, NewsSitemap, PageSitemap
from sitemaps import PhotoSetSitemap, ImageSitemap, StorySitemap

sitemaps = {
    'article_sitemap': ArticleSitemap,
    'news_sitemap': NewsSitemap,
    'page_sitemap': PageSitemap,
    'photoset_sitemap': PhotoSetSitemap,
    'image_sitemap': ImageSitemap,
    'story_sitemap': StorySitemap, 
}

urlpatterns = patterns('',
    (r'^$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps})
)