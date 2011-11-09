from django.contrib import admin
from django.utils.encoding import iri_to_uri
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.urlresolvers import reverse

from event_logs.models import EventLog
from perms.utils import update_perms_and_save
from attorneys.models import Attorney, Photo
from attorneys.forms import AttorneyForm, PhotoForm

class PhotoInline(admin.StackedInline):
    model = Photo
    form = PhotoForm
    fieldsets = (
        (None, {'fields': (
            'file',
        )}),
    )
    extra = 0;

class AttorneyAdmin(admin.ModelAdmin):
    class Meta:
        model = Attorney
        
    list_display = ['view_on_site', 'edit_link', "last_name", "first_name", "position", "category", "ordering"]
    list_filter = ["category"]
    prepopulated_fields = {'slug': ['first_name','last_name']}
    form = AttorneyForm
    ordering = ['ordering']
    list_editable = ['ordering']
    inlines = [PhotoInline,]
    
    fieldsets = (
        (None, {'fields': (
            'first_name',
            'middle_initial',
            'last_name',
            'slug',
            'category',
            'position',
            'address',
            'address2',
            'city',
            'state',
            'zip',
            'phone',
            'fax',
            'email',
            'bio',
            'education',
            'casework',
            'admissions',
            'tags',
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

    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:attorneys_attorney_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'

    def view_on_site(self, obj):
        link_icon = '%s/images/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('attorneys.detail', args=[obj.slug]),
            obj.name,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'
    
    def log_deletion(self, request, object, object_repr):
        super(AttorneyAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 493000,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(AttorneyAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 492000,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(AttorneyAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 491000,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, 
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
         
    def save_formset(self, request, form, formset, change):
        for f in formset.forms:
            file = f.save(commit=False)
            if file.file:
                file.attorney = form.save()
                file.content_type = ContentType.objects.get_for_model(file.attorney)
                file.object_id = file.attorney.pk
                file.name = file.file.name
                file.creator = request.user
                file.owner = request.user
                file.save()

        formset.save()

    def get_form(self, request, obj=None, **kwargs):
        """
        inject the user in the form.
        """
        form = super(AttorneyAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def save_model(self, request, object, form, change):
        """
        update the permissions backend
        """
        instance = form.save(commit=False)
        instance = update_perms_and_save(request, form, instance)
        return instance

    def change_view(self, request, object_id, extra_context=None):
		result = super(AttorneyAdmin, self).change_view(request, object_id, extra_context)

		if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
			result['Location'] = iri_to_uri("%s") % request.GET.get('next')
		return result

admin.site.register(Attorney, AttorneyAdmin)
