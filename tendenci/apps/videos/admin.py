from django.contrib import admin
from django.conf import settings

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.videos.models import Video, Category, VideoType
from tendenci.apps.videos.forms import VideoForm


class VideoInline(admin.TabularInline):
    model = Video
    max_num = 0
    can_delete = False
    fields = ('title', 'tags')
    readonly_fields = ('title', 'tags')


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    inlines = [VideoInline]


class VideoAdmin(TendenciBaseModelAdmin):

    list_display = ['title', 'tags', 'category', 'video_type', 'ordering']
    list_editable = ['ordering']
    prepopulated_fields = {'slug': ['title']}
    search_fields = ['question', 'answer']
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'category', 'video_type', 'image', 'clear_image', 'video_url', 'tags', 'description')}),
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
    ordering = ['-ordering']

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/jquery-1.6.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery-ui-1.8.17.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder-ordering.js' % settings.STATIC_URL,
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
admin.site.register(VideoType, CategoryAdmin)
