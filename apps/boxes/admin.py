from django.contrib import admin
from django.utils.encoding import iri_to_uri
from django.core.urlresolvers import reverse
from django.conf import settings

from event_logs.models import EventLog
from perms.utils import is_admin, get_notice_recipients, update_perms_and_save
from boxes.models import Box 
from boxes.forms import BoxForm


class BoxAdmin(admin.ModelAdmin):
    list_display = ('edit_link', 'pk', 'title', 'tags', 'content', 'admin_perms', 'admin_status')
    search_fields = ('title','content','tags',)
    fieldsets = (
        (None, {'fields': ('title', 'content', 'tags')}),
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
    form = BoxForm

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )

    def admin_status(self, obj):
        return obj.obj_status
    admin_status.allow_tags = True
    admin_status.short_description = 'status'

    def admin_perms(self, obj):
        return obj.obj_perms
    admin_perms.allow_tags = True
    admin_perms.short_description = 'permission'

    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:boxes_box_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'

    def log_deletion(self, request, object, object_repr):
        super(BoxAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 1100300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(BoxAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 1100200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(BoxAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 1100100,
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
   
        # update all permissions and save the model
        instance = update_perms_and_save(request, form, instance)
        
        return instance
    
    def change_view(self, request, object_id, extra_context=None):
        result = super(BoxAdmin, self).change_view(request, object_id, extra_context)

        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

admin.site.register(Box, BoxAdmin)