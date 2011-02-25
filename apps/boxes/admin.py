from django.contrib import admin
from django.utils.encoding import iri_to_uri

from event_logs.models import EventLog
from perms.models import ObjectPermission
from perms.utils import is_admin, get_notice_recipients
from boxes.models import Box 
from boxes.forms import BoxForm

    
class BoxAdmin(admin.ModelAdmin):
    list_display = ('title','pk', 'tags')
    search_fields = ('title','content','tags',)
    fieldsets = (
        (None, {'fields': ('title', 'content', 'tags')}),
        ('Administrative', {'fields': (
            'allow_anonymous_view','user_perms','group_perms','status','status_detail' )}),
    )
    form = BoxForm

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )

    def log_deletion(self, request, object, object_repr):
        super(BoxAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 1101000,
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
            'event_id' : 1102000,
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
            'event_id' : 1100000,
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

        # setup user permission
        instance.allow_user_view, instance.allow_user_edit = form.cleaned_data['user_perms']
        
        # row level user
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username    
                
        # save the object
        instance.save()

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
    
    def change_view(self, request, object_id, extra_context=None):
		result = super(BoxAdmin, self).change_view(request, object_id, extra_context)

		if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
			result['Location'] = iri_to_uri("%s") % request.GET.get('next')
		return result

admin.site.register(Box, BoxAdmin)