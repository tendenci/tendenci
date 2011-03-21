from django.conf.urls.defaults import patterns
from sitemaps import views

#------------------------------------------------------------------ sitemaps = {
    #---------------------------------------------- 'page_sitemap': PageSitemap,
    #---------------------------------------- 'article_sitemap': ArticleSitemap,
    #---------------------------------------------- 'news_sitemap': NewsSitemap,
    #-------------------------------------- 'photoset_sitemap': PhotoSetSitemap,
    #-------------------------------------------- 'image_sitemap': ImageSitemap,
#------------------------------------------- #    'story_sitemap': StorySitemap,
#----------------------------------------------------------------------------- }

urlpatterns = patterns('',
    (r'^$', views.create_sitemap)
)
