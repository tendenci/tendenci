from __future__ import absolute_import
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from .models import Speaker, SpeakerFile, Track
from .forms import SpeakerForm, FileForm


class FileAdmin(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': (
            'file',
            'photo_type',
            'description',
            'position',
        )},),
    )
    model = SpeakerFile
    form = FileForm
    extra = 0


class SpeakerAdmin(TendenciBaseModelAdmin):
    list_display = ['name', 'track', 'company', 'position', 'ordering']
    list_filter = ['company', 'track']
    search_fields = ['name', 'biography']
    ordering = ('ordering',)
    prepopulated_fields = {'slug': ['name']}
    fieldsets = (
        (None, {'fields': (
            'name',
            'slug',
            'company',
            'position',
            'track',
            'ordering',
            'biography',
            'email',
            'personal_sites',
            'tags'
        )}),
        ('Social Media', {
        'description': ('Enter just your usernames for any of these social media sites. No need to enter the full links.'),
        'fields': (
             ('facebook',), ('twitter',), ('linkedin',), ('get_satisfaction'),
             ('flickr',), ('slideshare',),
        )}),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'status',
            'status_detail',
        )}),
    )
    form = SpeakerForm
    inlines = (FileAdmin,)

    def __init__(self, *args, **kwargs):
        super(SpeakerAdmin, self).__init__(*args, **kwargs)
        self.list_editable = ['name', 'ordering']

    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder-ordering.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }

    def save_formset(self, request, form, formset, change):

        for f in formset.forms:
            file = f.save(commit=False)
            if file.file:
                file.speaker = form.save()
                file.content_type = ContentType.objects.get_for_model(file.speaker)
                file.object_id = file.speaker.pk
                file.name = file.file.name
                file.creator = request.user
                file.owner = request.user
                file.save(log=False)

        formset.save()

class TrackAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Speaker, SpeakerAdmin)
admin.site.register(Track, TrackAdmin)
