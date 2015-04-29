from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.photos.models import PhotoSet, Image, Pool
from tendenci.apps.photos.forms import PhotoSet, PhotoAdminForm, PhotoSetAddForm

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import get_notice_recipients, update_perms_and_save
from tendenci.apps.notifications.context_processors import notification

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('name', 'update_dt', 'create_dt', 'tags', 'position')
    list_editable = ['tags', 'position']
    fieldsets = (
        (_('Photo Set Information'), {
                      'fields': ('name',
                                 'description',
                                 'group',
                                 'tags',
                                 ),
                      }),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
            )}),
        (_('Photo Set Status'), {'fields': (
            'status_detail',
        )}),
    )
    form = PhotoSetAddForm
    ordering = ['position']
    
    class Media:
        css = {
            "all": ("css/websymbols.css",)
        }
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.11.0/jquery-ui.min.js',
            'js/admin/admin-list-reorder.js',
        )


    def log_deletion(self, request, object, object_repr):
        super(PhotoAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 990300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name,
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def log_change(self, request, object, message):
        super(PhotoAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 990200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name,
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def log_addition(self, request, object):
        super(PhotoAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 990100,
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

        # notifications
        if not request.user.profile.is_superuser:
            # send notification to administrators
            recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': instance,
                        'request': request,
                    }
                    notification.send_emails(recipients, notice_type, extra_context)

        return instance

admin.site.register(PhotoSet, PhotoAdmin) #Image,
