from django.contrib import admin
from tendenci.core.registry import admin_registry
from tendenci.addons.articles.models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['headline','create_dt']

#admin_registry.site.register(Article, ArticleAdmin)