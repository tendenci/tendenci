from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.help_files.models import Topic, HelpFile, Request
from tendenci.apps.help_files.forms import HelpFileAdminForm
from tendenci.apps.theme.templatetags.static import static


class HelpFileAdmin(TendenciBaseModelAdmin):

    list_display = ['question', 'level', 'status_detail', 'view_totals']
    list_filter = ['topics', 'level', 'is_faq', 'is_featured', 'is_video', 'syndicate']
    filter_horizontal = ['topics']
    search_fields = ['question', 'answer']
    fieldsets = (
        (None, {'fields': ('question', 'slug', 'answer', 'group', 'level', 'topics')}),
        (_('Flags'), {'fields': (
            'is_faq', 'is_featured', 'is_video', 'syndicate',)}),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        (_('Publishing Status'), {'fields': (
            'status_detail',
        )}),
    )
    prepopulated_fields = {'slug': ['question']}
    form = HelpFileAdminForm

    class Media:
        js = (
            static('js/global/tinymce.event_handlers.js'),
        )

admin.site.register(Topic)
admin.site.register(HelpFile, HelpFileAdmin)
admin.site.register(Request)
