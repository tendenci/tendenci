from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.stories.models import Story, Rotator
from tendenci.apps.stories.forms import StoryAdminForm
from tendenci.apps.stories.utils import copy_story
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import update_perms_and_save


class StoryAdmin(TendenciBaseModelAdmin):
    list_display = ('image_preview', 'title', 'tags', 'status', 'position')
    search_fields = ('title', 'content')
    list_editable = ['title', 'tags', 'position']
    actions = ['clone_story']
    fieldsets = [(_('Story Information'), {
                      'fields': ['title',
                                 'content',
                                 'photo_upload',
                                 'full_story_link',
                                 'link_title',
                                 'rotator',
                                 'tags',
                                 'start_dt',
                                 'end_dt',
                                 'expires'
                                 ],
                      }),
                    (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
                    (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
                        'user_perms',
                        'member_perms',
                        'group_perms',
                    )}),
                     (_('Administrator Only'), {
                      'fields': ['syndicate',
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
            '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.11.0/jquery-ui.min.js',
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
            alt = "%s" % obj.image
            if len(alt) > 123:
                alt = alt[:123]
            return '<img src="%s" alt="%s" title="%s" />' % (reverse('file', args=args), alt, alt)
        else:
            return _("No image")
    image_preview.allow_tags = True
    image_preview.short_description = _('Image')

    def clone_story(self, request, queryset):
        for story in queryset:
            copy_story(story, request.user)
    clone_story.short_description = _("Clone selected stories")


class StoryInline(admin.TabularInline):
    model = Story
    max_num = 0
    can_delete = False
    fields = ('image_preview','title','tags','rotator_position')
    readonly_fields = ('image_preview','title')
    ordering = ('rotator_position','title')

    def image_preview(self, obj):
        if obj.image:
            args = [obj.image.pk]
            args.append("100x50")
            args.append("crop")
            alt = "%s" % obj.image
            if len(alt) > 123:
                alt = alt[:123]
            return '<img src="%s" alt="%s" title="%s" />' % (reverse('file', args=args), alt, alt)
        else:
            return _("No image")
    image_preview.allow_tags = True
    image_preview.short_description = _('Image')


class RotatorAdmin(admin.ModelAdmin):
    inlines = [StoryInline]

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.11.0/jquery-ui.min.js',
            'js/admin/rotator-story-inline-ordering.js',
        )
        css = {'all': ['css/admin/dynamic-inlines-with-sort.css'], }


admin.site.register(Story, StoryAdmin)
admin.site.register(Rotator, RotatorAdmin)
