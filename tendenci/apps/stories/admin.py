from django.contrib import admin

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.stories.models import Story
from tendenci.apps.stories.forms import StoryAdminForm

class StoryAdmin(TendenciBaseModelAdmin):
    list_display = ('title', 'tags', 'status', 'ncsortorder')
    search_fields = ('title', 'content')
    list_editable = ['ncsortorder']
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
    ordering = ['-ncsortorder']

    class Media:
        css = {
            "all": ("css/websymbols.css",)
        }
        js = (
            'js/jquery-1.6.2.min.js',
            'js/jquery-ui-1.8.17.custom.min.js',
            'js/story-admin-list-reorder.js',
            'js/global/tinymce.event_handlers.js',
        )
    
    def save(self, *args, **kwargs):
        story = form.save(commit=False)
        story = update_perms_and_save(request, form, story)
 
        # save photo
        photo = form.cleaned_data['image']
        if photo:
            story.save(image=photo)
        log_defaults = {
            'instance': object,
            'action': "edit"
        }
        if not change:
            log_defaults['action'] = "add"
 
        # Handle a special case for bulk reordering via the list view.
        if form.changed_data != ['ncsortorder']:
            EventLog.objects.log(**log_defaults)
        return instance

admin.site.register(Story, StoryAdmin)
