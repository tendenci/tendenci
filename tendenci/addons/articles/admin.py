from django.contrib import admin
from tendenci.addons.articles.models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['headline','create_dt']

#admin.site.register(Article, ArticleAdmin)