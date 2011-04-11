from django.contrib import admin

from event_logs.models import EventLog
from perms.utils import update_perms_and_save
from models import Topic, HelpFile, Request
from forms import HelpFileForm
import settings

class HelpFileAdmin(admin.ModelAdmin):
    list_display = ['question', 'level', 'is_faq', 'is_featured', 'is_video', 'syndicate', 'view_totals']
    list_filter = ['topics', 'level', 'is_faq', 'is_featured', 'is_video', 'syndicate']
    filter_horizontal = ['topics']
    search_fields = ['question','answer']
    fieldsets = (
        (None, {'fields': ('question', 'slug', 'answer', 'level','topics','entity')}),
        ('Flags', {'fields': (
            ('is_faq', 'is_featured', 'is_video', 'syndicate'),)}),
        ('Administrative', {'fields': (
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail'
        )}),
    )
    prepopulated_fields = {'slug': ['question']}
    form = HelpFileForm

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )

    def log_deletion(self, request, object, object_repr):
        super(HelpFileAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 1000300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(HelpFileAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 1000200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(HelpFileAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 1000100,
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

        instance = update_perms_and_save(request, form, instance)
 
        # save the object
        form.save_m2m()
        
        return instance
    
admin.site.register(Topic)
admin.site.register(HelpFile, HelpFileAdmin)
admin.site.register(Request)
