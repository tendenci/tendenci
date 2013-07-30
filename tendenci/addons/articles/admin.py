from django.contrib import admin
from django.template.defaultfilters import striptags, truncatewords

from tendenci.core.perms.admin import TendenciBaseModelAdmin, TagsFilter
from tendenci.addons.articles.models import Article
from tendenci.addons.articles.forms import ArticleForm


class ArticleAdmin(TendenciBaseModelAdmin):
    list_display = ['headline', 'article_body', 'tags', 'update_dt', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status_detail', 'owner_username', TagsFilter]
    prepopulated_fields = {'slug': ['headline']}
    search_fields = ['headline', 'body']
    fieldsets = (
        ('Article Information', {
            'fields': ('headline',
                'slug',
                'summary',
                'body',
                'group',
                'tags',
                'source',
                'website',
                'release_dt',
                'timezone',
                )
            }),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'syndicate',
            'status_detail',
        )}),
    )
    form = ArticleForm
    ordering = ['-update_dt']

    def article_body(self, obj):
        content = truncatewords(striptags(obj.body), 15)
        return content
    article_body.allow_tags = True
    article_body.short_description = 'body'

admin.site.register(Article, ArticleAdmin)
