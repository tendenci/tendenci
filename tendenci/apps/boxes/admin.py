from django.contrib import admin
from django.conf import settings
from django.template.defaultfilters import truncatewords_html
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.boxes.models import Box
from tendenci.apps.boxes.forms import BoxForm


class BoxAdmin(TendenciBaseModelAdmin):
    list_display = ('edit_link', 'pk', 'title', 'group', 'tags', 'short_content', 'admin_perms', 'status', 'position')
    search_fields = ('title', 'content', 'tags', 'group', )
    list_editable = ['title', 'tags', 'status', 'position', 'group']
    list_filter = ('group', )
    fieldsets = (
        (None, {'fields': ('title', 'content', 'group', 'tags')}),
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
    view_on_site = False
    form = BoxForm
    ordering = ['-position']

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.11.0/jquery-ui.min.js',
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )

    def admin_status(self, obj):
        return obj.obj_status
    admin_status.allow_tags = True
    admin_status.short_description = _('status')

    def admin_perms(self, obj):
        return obj.obj_perms
    admin_perms.allow_tags = True
    admin_perms.short_description = _('permission')

    def short_content(self, obj):
        return '<div style="max-width: 600px; overflow: hidden;">%s</div>' % truncatewords_html(obj.content, 30)
    short_content.allow_tags = True
    short_content.short_description = _('content')

admin.site.register(Box, BoxAdmin)
