from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.conf import settings

from event_logs.models import EventLog
from perms.utils import update_perms_and_save
from models import Topic, HelpFile, Request
from forms import HelpFileAdminForm

class HelpFileAdmin(admin.ModelAdmin):
    list_display = ['view_on_site', 'edit_link', 'question', 'level', 'status_detail', 'view_totals']
    list_filter = ['topics', 'level', 'is_faq', 'is_featured', 'is_video', 'syndicate']
    filter_horizontal = ['topics']
    search_fields = ['question','answer']
    fieldsets = (
        (None, {'fields': ('question', 'slug', 'answer', 'level','topics','entity')}),
        ('Flags', {'fields': (
            ('is_faq', 'is_featured', 'is_video', 'syndicate'),)}),
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
    prepopulated_fields = {'slug': ['question']}
    form = HelpFileAdminForm

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:help_files_helpfile_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'

    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('help_file.details', args=[obj.slug]),
            obj.question,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'
    
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
    
    def change_view(self, request, object_id, extra_context=None):
		result = super(HelpFileAdmin, self).change_view(request, object_id, extra_context)

		if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
			result['Location'] = iri_to_uri("%s") % request.GET.get('next')
		return result
    
admin.site.register(Topic)
admin.site.register(HelpFile, HelpFileAdmin)
admin.site.register(Request)
