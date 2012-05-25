from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.conf import settings

from event_logs.models import EventLog
from perms.object_perms import ObjectPermission
from models import Speaker, SpeakerFile
from forms import SpeakerForm, FileForm

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

class SpeakerAdmin(admin.ModelAdmin):
    list_display = ['view_on_site', 'edit_link', 'ordering', 'name', 'track', 'company', 'position']
    list_filter = ['company', 'track']
    search_fields = ['name','biography']
    ordering = ('-ordering',)
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
             ('facebook','twitter','linkedin','get_satisfaction','flickr','slideshare'),
        )}),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',),'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'status',
            'status_detail'
        )}),
    )
    form = SpeakerForm
    inlines = (FileAdmin,)

    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/speaker-dynamic-sort.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }

    
    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('speaker.view', args=[obj.slug]),
            obj.name,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'
    
    
    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:speakers_speaker_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'
    
    
    def years(self, obj):
        return obj.years()

    def log_deletion(self, request, object, object_repr):
        super(SpeakerAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 1070300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name,
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def log_change(self, request, object, message):
        super(SpeakerAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 1070200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name,
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
        
    def log_addition(self, request, object):
        super(SpeakerAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 1070100,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name,
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)

        # set up user permission
        instance.allow_user_view, instance.allow_user_edit = form.cleaned_data['user_perms']

        # adding the quote
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username

        # save the object
        instance.save()
        form.save_m2m()

        # permissions
        if not change:
            # assign permissions for selected groups
            ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], instance)
            # assign creator permissions
            ObjectPermission.objects.assign(instance.creator, instance)
        else:
            # assign permissions
            ObjectPermission.objects.remove_all(instance)
            ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], instance)
            ObjectPermission.objects.assign(instance.creator, instance)

        return instance

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
                file.save()

        formset.save()

    def change_view(self, request, object_id, extra_context=None):
		result = super(SpeakerAdmin, self).change_view(request, object_id, extra_context)

		if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
			result['Location'] = iri_to_uri("%s") % request.GET.get('next')
		return result

admin.site.register(Speaker, SpeakerAdmin)
