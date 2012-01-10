from django.contrib import admin
from django.conf import settings

from events.models import CustomRegForm, CustomRegField
from events.forms import CustomRegFormAdminForm, CustomRegFormForField 
from event_logs.models import EventLog

class EventAdmin(admin.ModelAdmin):
#    form = EventForm
    list_display=(
        'title',
        'description', 
        'start_dt',
        'end_dt',
        'timezone',
        'allow_anonymous_view',
        'allow_user_view',
        'allow_user_edit',
        'status',
        'status_detail',
    )

#admin.site.register(Event, EventAdmin)
#admin.site.register(Type)

class CustomRegFieldAdminForm(CustomRegFormForField):
    class Meta:
        model = CustomRegField

    
class CustomRegFieldAdmin(admin.TabularInline):
    model = CustomRegField    
    form = CustomRegFieldAdminForm
    extra = 0
    ordering = ("position",)

class CustomRegFormAdmin(admin.ModelAdmin):
    inlines = (CustomRegFieldAdmin,)
    list_display = ("name", "notes", "status",)
    search_fields = ("name", "notes", "status",)
#    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = (
        (None, {"fields": ("name", "notes", 'status')}),
    )
    
    form = CustomRegFormAdminForm
    
    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/form-fields-inline-ordering.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }
        
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
         
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            
        instance.owner = request.user
        instance.owner_username = request.user.username
        print instance.creator
        print instance.owner
        # save the object
        instance.save()
        
        form.save_m2m()
        
        return instance
    
    def log_deletion(self, request, object, object_repr):
        super(CustomRegFormAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 176300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
    
    def log_change(self, request, object, message):
        super(CustomRegFormAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 176200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
    
    def log_addition(self, request, object):
        super(CustomRegFormAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 176100,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, 
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
        
        
admin.site.register(CustomRegForm, CustomRegFormAdmin)
