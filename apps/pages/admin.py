from django.contrib import admin

from event_logs.models import EventLog
from perms.utils import is_admin, get_notice_recipients
from perms.utils import update_perms_and_save
from models import Page 
from forms import PageAdminForm
import settings

try:
    from notification import models as notification
except:
    notification = None
    
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'syndicate', 
                    'allow_anonymous_view', 'status', 
                    'status_detail')
    search_fields = ('title','content',)
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'content', 'tags')}),
        ('Flags', {'fields': 
            ('syndicate',)}),
        ('Administrative', {'fields': (
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail'
        )}),
    )
    prepopulated_fields = {'slug': ['title']}
    form = PageAdminForm

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )

    def link(self, obj):
        return '<a href="%s" title="%s">%s</a>' % (
            obj.get_absolute_url(),
            obj.title,
            obj.slug                                         
        )
    link.allow_tags = True

    def log_deletion(self, request, object, object_repr):
        super(PageAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 583000,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(PageAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 582000,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(PageAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 581000,
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
        
        # notifications
        if not is_admin(request.user):
            # send notification to administrators
            recipients = get_notice_recipients('module', 'pages', 'pagerecipients')
            notice_type = 'page_added'
            if change: notice_type = 'page_edited' 
            if recipients:
                if notification:
                    extra_context = {
                        'object': instance,
                        'request': request,
                    }
                    notification.send_emails(recipients, notice_type, extra_context)

        return instance

admin.site.register(Page, PageAdmin)