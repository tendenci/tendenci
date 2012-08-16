from django.contrib import admin
from django.conf import settings
from django.core.urlresolvers import reverse

from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.utils import update_perms_and_save
from tendenci.addons.culintro.models import CulintroJob
from tendenci.addons.culintro.forms import CulintroJobForm

class CulintroJobAdmin(admin.ModelAdmin):
    list_display = [u'title', 'view_on_site', 'edit_link', 'tags']
    list_filter = []
    search_fields = []
    actions = []
    prepopulated_fields = {'slug': ['title']}

    form = CulintroJobForm

    fieldsets = [(None, {
                      'fields': ['title',
                                'slug',
                                'description',
                                'location_2',
                                'location_other',
                                'tags',
                                'pricing',
                                'activation_dt',
                                'expiration_dt',
                                'post_dt',
                                'contact_name',
                                'contact_email',
                                'contact_phone',
                                'open_call',
                                'promote_posting',
                                 ],
                      }),
                      ('Payment', {
                      'fields': ['list_type',
                                 'payment_method'
                                 ],
                      })]

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
    
    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:culintro_culintrojob_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'

    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('culintro.detail', args=[obj.slug]),
            obj,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'

    def log_deletion(self, request, object, object_repr):
        super(CulintroJobAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 1180300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(CulintroJobAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 1180200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(CulintroJobAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 1180100,
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
        form = super(CulintroJobAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form
        
    def save_model(self, request, object, form, change):
        """
        update the permissions backend
        """
        instance = form.save(commit=False)
        perms = update_perms_and_save(request, form, instance)
        return instance

    def save_form(self, request, form, change):
        if form.is_valid():
            obj = super(CulintroJobAdmin, self).save_form(request, form, change)
            return obj
        
        return None

    def change_view(self, request, object_id, extra_context=None):
        result = super(CulintroJobAdmin, self).change_view(request, object_id, extra_context)

        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

admin.site.register(CulintroJob, CulintroJobAdmin)
