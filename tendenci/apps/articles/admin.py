from django.contrib import admin
from django.template.defaultfilters import striptags, truncatewords
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from tendenci.apps.perms.admin import TendenciBaseModelAdmin, TagsFilter
from tendenci.apps.articles.models import Article
from tendenci.apps.articles.forms import ArticleForm


class ArticleAdmin(TendenciBaseModelAdmin):
    list_display = ['headline', 'article_body', 'tags', 'update_dt', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status_detail', 'owner_username', TagsFilter]
    prepopulated_fields = {'slug': ['headline']}
    search_fields = ['headline', 'body']
    fieldsets = (
        (_('Article Information'), {
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
        (_('Author'), {
            'fields': ('first_name',
                     'last_name',
                     'phone',
                     'fax',
                     'email',
                     ),
                    'classes': ('contact',),
        }),
        (_('Contributor'), {
            'fields': ('contributor_type',
                     ),
                    'classes': ('contact',),
        }),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        (_('Publishing Status'), {'fields': (
            'syndicate',
            'status_detail',
        )}),
    )
    form = ArticleForm
    ordering = ['-update_dt']

    @mark_safe
    def article_body(self, obj):
        content = truncatewords(striptags(obj.body), 15)
        return content
    article_body.short_description = _('body')

admin.site.register(Article, ArticleAdmin)
