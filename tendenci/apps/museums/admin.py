from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.museums.models import Museum, Photo
from tendenci.apps.museums.forms import MuseumForm, PhotoForm

class PhotoAdmin(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': (
            'file',
        )},),
    )
    model = Photo
    form = PhotoForm

class MuseumAdmin(TendenciBaseModelAdmin):
    list_display = [u'name', 'ordering']
    list_filter = []
    filter_horizontal = ['special_offers']
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
            photo.save(log=False)

admin.site.register(Museum, MuseumAdmin)
