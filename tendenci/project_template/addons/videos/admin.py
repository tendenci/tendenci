from django.contrib import admin
from django.conf import settings

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from addons.videos.models import Video, Category
from addons.videos.forms import VideoForm


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}


class VideoAdmin(TendenciBaseModelAdmin):

    list_display = ['title', 'category', 'ordering']
    list_filter = ['category']
    list_editable = ['ordering']
    prepopulated_fields = {'slug': ['title']}
    search_fields = ['question', 'answer']
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'category', 'image', 'clear_image', 'video_url', 'tags', 'description')}),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'status',
            'status_detail'
        )}),
    )
    form = VideoForm
    ordering = ['-ordering']

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/jquery-1.6.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery-ui-1.8.17.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
        )
    
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
