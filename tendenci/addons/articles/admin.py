from django.contrib import admin

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.addons.articles.models import Article
from tendenci.addons.articles.forms import ArticleForm


class ArticleAdmin(TendenciBaseModelAdmin):
    list_display = ['headline', 'update_dt', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status_detail', 'owner_username']
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
            'status',
            'status_detail',
        )}),
    )
    form = ArticleForm
    ordering = ['-update_dt']

admin.site.register(Article, ArticleAdmin)
