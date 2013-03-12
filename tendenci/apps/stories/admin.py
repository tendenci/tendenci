from django.contrib import admin
from django.core.urlresolvers import reverse

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.stories.models import Story
from tendenci.apps.stories.forms import StoryAdminForm
from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.utils import update_perms_and_save


class StoryAdmin(TendenciBaseModelAdmin):
    list_display = ('image_preview', 'title', 'tags', 'status', 'position')
    search_fields = ('title', 'content')
    list_editable = ['title', 'tags', 'position']
    fieldsets = [('Story Information', {
                      'fields': ['title',
                                 'content',
                                 'photo_upload',
                                 'full_story_link',
                                 'link_title',
                                 'tags',
                                 'start_dt',
                                 'end_dt',
                                 'expires'
                                 ],
                      }),
                    ('Permissions', {'fields': ('allow_anonymous_view',)}),
                    ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
                        'user_perms',
                        'member_perms',
                        'group_perms',
                    )}),
                     ('Administrator Only', {
                      'fields': ['syndicate',
                                 'status',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]
    form = StoryAdminForm
    ordering = ['-position']

    class Media:
        css = {
            "all": ("css/websymbols.css",)
        }
        js = (
            'js/jquery-1.6.2.min.js',
            'js/jquery-ui-1.8.17.custom.min.js',
            'js/admin/admin-list-reorder.js',
            'js/global/tinymce.event_handlers.js',
        )
    
    def save_model(self, request, object, form, change):
        story = form.save(commit=False)

        # save photo
        if 'photo_upload' in form.cleaned_data:
            photo = form.cleaned_data['photo_upload']
            if photo:
                story.save(photo=photo)

        story = update_perms_and_save(request, form, story)

        log_defaults = {
            'instance': object,
            'action': "edit"
        }
        if not change:
            log_defaults['action'] = "add"

        # Handle a special case for bulk reordering via the list view.
        if form.changed_data != ['position']:
            EventLog.objects.log(**log_defaults)
        return object

    def image_preview(self, obj):
        if obj.image:
            args = [obj.image.pk]
            args.append("100x50")
            args.append("crop")
            return '<img src="%s" />' % reverse('file', args=args)
        else:
            return "No image"
    image_preview.allow_tags = True
    image_preview.short_description = 'Image'

admin.site.register(Story, StoryAdmin)
