from django.contrib import admin
from django.template.defaultfilters import truncatewords_html
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.boxes.models import Box
from tendenci.apps.boxes.forms import BoxForm
from tendenci.apps.theme.templatetags.static import static


class BoxAdmin(TendenciBaseModelAdmin):
    list_display = ('edit_link', 'pk', 'title', 'group', 'tags', 'short_content', 'admin_perms', 'status', 'position')
    search_fields = ('title', 'content', 'tags', 'group__name', )
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
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/admin/admin-list-reorder.js'),
            static('js/global/tinymce.event_handlers.js'),
        )

    @mark_safe
    def admin_status(self, obj):
        return obj.obj_status
    admin_status.short_description = _('status')

    @mark_safe
    def admin_perms(self, obj):
        return obj.obj_perms
    admin_perms.short_description = _('permission')

    @mark_safe
    def short_content(self, obj):
        return '<div style="max-width: 600px; overflow: hidden;">%s</div>' % truncatewords_html(obj.content, 30)
    short_content.short_description = _('content')

admin.site.register(Box, BoxAdmin)
