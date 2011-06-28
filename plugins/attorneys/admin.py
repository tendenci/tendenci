from django.contrib import admin
from django.conf import settings
from django.core.urlresolvers import reverse

from event_logs.models import EventLog
from perms.object_perms import ObjectPermission
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
        
    list_display = ['view_on_site', 'edit_link',  "last_name", "first_name", "position", "category"]
    list_filter = ["category"]
    prepopulated_fields = {'slug': ['first_name','last_name']}
    form = AttorneyForm
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
        ('Administrative', {'fields': (
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail'
        )}),
    )
            
    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
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
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:
                instance.creator = request.user
                instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
            instance.save()
    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)

        # set up user permission
        instance.allow_user_view, instance.allow_user_edit = form.cleaned_data['user_perms']
        
        # adding the attorney
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
 
        # save the object
        instance.save()
        form.save_m2m()

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
    
    def get_form(self, request, obj=None, **kwargs):
        """
        inject the user in the form.
        """
        form = super(AttorneyAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

admin.site.register(Attorney, AttorneyAdmin)
