from django.contrib import admin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.contrib.contenttypes.models import ContentType

from event_logs.models import EventLog
from perms.utils import update_perms_and_save
from museums.models import Museum, Photo
from museums.forms import MuseumForm, PhotoForm

class PhotoAdmin(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': (
            'file',
        )},),
    )
    model = Photo
    form = PhotoForm

class MuseumAdmin(admin.ModelAdmin):
    list_display = ['view_on_site', 'edit_link', u'name', 'ordering']
    list_filter = []
    search_fields = ['name', 'about']
    list_editable = ['ordering']
    prepopulated_fields = {'slug': ['name']}
    ordering = ['ordering']
    actions = []
    inlines = (PhotoAdmin,)
    form = MuseumForm
    
    fieldsets = (
        ('Basic Information', {'fields': (
            'name',
            'slug',
            'phone',
            'address',
            'city',
            'state',
            'zip',
            'website',
            'building_photo',
            'about'
        )}),
        ('Visitor Information', {'fields': (
            'hours',
            'free_times',
            'parking_information',
            'free_parking',
            'street_parking',
            'paid_parking',
            'dining_information',
            'restaurant',
            'snacks',
            'shopping_information',
            'events',
            'special_offers',
        )}),
        ('Social Media', {'fields': (
            'facebook',
            'twitter',
            'flickr',
            'youtube',
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
    
    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/jquery-1.6.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery-ui-1.8.2.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
        )
    
    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:museums_museum_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'

    def view_on_site(self, obj):
        link_icon = '%s/images/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('museums.detail', args=[obj.slug]),
            obj,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'

    def log_deletion(self, request, object, object_repr):
        super(MuseumAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 1140300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(MuseumAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 1140200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(MuseumAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 1140100,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, 
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
                     
    def get_form(self, request, obj=None, **kwargs):
        """
        inject the user in the form.
        """
        form = super(MuseumAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def save_model(self, request, object, form, change):
        """
        update the permissions backend
        """
        instance = form.save(commit=False)
        perms = update_perms_and_save(request, form, instance)
        return instance
        
    def save_formset(self, request, form, formset, change):
        """
        Associate the user to each photo saved.
        """
        photos = formset.save(commit=False)
        for photo in photos:
            photo.content_type = ContentType.objects.get_for_model(photo.museum)
            photo.object_id = photo.museum.pk
            photo.name = photo.file.name
            photo.creator = request.user
            photo.owner = request.user
            photo.save()

    def change_view(self, request, object_id, extra_context=None):
        result = super(MuseumAdmin, self).change_view(request, object_id, extra_context)

        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

admin.site.register(Museum, MuseumAdmin)
