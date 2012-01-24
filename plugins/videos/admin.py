from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.conf import settings

from event_logs.models import EventLog
from perms.utils import update_perms_and_save
from perms.object_perms import ObjectPermission
from models import Video, Category
from forms import VideoForm
    
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    

class VideoAdmin(admin.ModelAdmin):

    list_display = ['view_on_site', 'edit_link' ,'title', 'category', 'ordering']
    list_filter = ['category']
    list_editable = ['ordering']
    prepopulated_fields = {'slug': ['title']}
    search_fields = ['question','answer']
    fieldsets = (
        (None, {'fields': ('title','slug','category','image','video_url','tags','description')}),
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
    form = VideoForm
    ordering = ['-ordering']

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/jquery-1.6.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery-ui-1.8.17.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
        )
    
    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:videos_video_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'
    
    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('video.details', args=[obj.slug]),
            obj.title,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'

    def log_deletion(self, request, object, object_repr):
        super(VideoAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 1200300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(VideoAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 1200200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(VideoAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 1200100,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, 
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
    
    def save_model(self, request, object, form, change):
        """
        update the permissions backend
        """
        instance = form.save(commit=False)
        instance = update_perms_and_save(request, form, instance)
        return instance

    def change_view(self, request, object_id, extra_context=None):
		result = super(VideoAdmin, self).change_view(request, object_id, extra_context)

		if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
			result['Location'] = iri_to_uri("%s") % request.GET.get('next')
		return result

admin.site.register(Video, VideoAdmin)
admin.site.register(Category, CategoryAdmin)