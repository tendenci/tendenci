from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri

from event_logs.models import EventLog
from perms.models import ObjectPermission
from models import Staff, Position, Department
from forms import StaffForm

class StaffAdmin(admin.ModelAdmin):
    list_display = ['staff_photo', 'name', 'department','position', 'start_date', 'years']
    list_filter = ['start_date']
    search_fields = ['name','biography']
    ordering = ('-start_date',)
    prepopulated_fields = {'slug': ['name']}
    fieldsets = (
        (None, {'fields': (
            'name',
            'slug',
            'photo',
            'start_date',
            'biography',
            'department',
            'position',
            'email',
            'phone',
            'tags'
        )}),
        ('Administrative', {'fields': (
            'allow_anonymous_view','user_perms','group_perms','status','status_detail' )}),
    )
    form = StaffForm

    def staff_photo(self, obj):
        return '<img src="%s" title="%s" />' % (
            reverse('staff.photo', args=[obj.pk, '48x48']),
            obj.name
        )
    staff_photo.allow_tags = True
    staff_photo.short_description = 'photo'

    def years(self, obj):
        return obj.years()

    def log_deletion(self, request, object, object_repr):
        super(StaffAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 1000300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name,
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        # EventLog.objects.log(**log_defaults)

    def log_change(self, request, object, message):
        super(StaffAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 1000200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name,
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        # EventLog.objects.log(**log_defaults)

    def log_addition(self, request, object):
        super(StaffAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 1000100,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name,
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        # EventLog.objects.log(**log_defaults)

    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)

        # set up user permission
        instance.allow_user_view, instance.allow_user_edit = form.cleaned_data['user_perms']

        # adding the quote
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

    def change_view(self, request, object_id, extra_context=None):
		result = super(StaffAdmin, self).change_view(request, object_id, extra_context)

		if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
			result['Location'] = iri_to_uri("%s") % request.GET.get('next')
		return result

admin.site.register(Staff, StaffAdmin)
admin.site.register(Department)
admin.site.register(Position)
