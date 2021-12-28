from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.videos.models import Video, Category, VideoType
from tendenci.apps.videos.forms import VideoForm
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.templatetags.static import static


class VideoInline(admin.TabularInline):
    model = Video
    max_num = 0
    can_delete = False
    fields = ('title', 'tags')
    readonly_fields = ('title', 'tags')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'position')
    list_editable = ['position', 'name']
    prepopulated_fields = {'slug': ['name']}
    inlines = [VideoInline]
    ordering = ('position',)

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/admin/admin-list-reorder.js'),
        )


class VideoTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    prepopulated_fields = {'slug': ['name']}


class VideoAdmin(TendenciBaseModelAdmin):
    def get_release_dt(self, instance):
        dt = instance.release_dt

        if dt:
            return dt.strftime('%x')
        return u''
    get_release_dt.short_description = _('Release Date')
    list_display = ['title', 'tags', 'category', 'video_type', 'get_release_dt', 'show_group', 'status_detail']
    list_editable = ['category', 'video_type']
    if not get_setting('module', 'videos', 'order_by_release_dt'):
        list_display.append('position')
        list_editable.append('position')
    prepopulated_fields = {'slug': ['title']}
    search_fields = ['title', 'description']
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'category', 'video_type', 'image', 'clear_image', 'video_url', 'group', 'tags', 'description', 'release_dt')}),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'status_detail',
        )}),
    )
    form = VideoForm
    if not get_setting('module', 'videos', 'order_by_release_dt'):
        ordering = ['-position']
    else:
        ordering = ['-release_dt']

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/admin/admin-list-reorder.js'),
            static('js/global/tinymce.event_handlers.js'),
        )

    @mark_safe
    def show_group(self, instance):
        if instance.group:
            return '<a href="{0}" title="{1}">{1}</a>'.format(
                    reverse('group.detail', args=[instance.group.slug]),
                    instance.group,
                    instance.group.id,
                )
        return ""
    show_group.short_description = 'Group'
    show_group.admin_order_field = 'group'

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(VideoAdmin, self).get_fieldsets(request, obj)
        if not obj or (obj and not obj.image):
            fields = list(fieldsets[0][1]['fields'])
            if 'clear_image' in fields:
                fields.remove('clear_image')
                fieldsets[0][1]['fields'] = tuple(fields)
        return fieldsets

admin.site.register(Video, VideoAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(VideoType, VideoTypeAdmin)
