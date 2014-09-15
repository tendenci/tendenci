from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.addons.news.models import News
from tendenci.addons.news.forms import NewsForm

class NewsAdmin(TendenciBaseModelAdmin):
    list_display = ['headline', 'update_dt', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status_detail', 'owner_username']
    prepopulated_fields = {'slug': ['headline']}
    search_fields = ['headline', 'body']
    fieldsets = (
        (_('News Information'), {
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
        (_('Contributor'), {'fields': ('contributor_type',)}),
        (_('Author'), {'fields': ('first_name',
                                 'last_name',
                                 'google_profile',
                                 'phone',
                                 'fax',
                                 'email',
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
    form = NewsForm
    ordering = ['-update_dt']

admin.site.register(News, NewsAdmin)
