from django.contrib.sitemaps import Sitemap

class TendenciSitemap(Sitemap):
    pass


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