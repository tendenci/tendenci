from django.contrib import admin
from django.utils.encoding import iri_to_uri
from django.utils.text import truncate_words
from django.utils.html import strip_tags
from django.core.urlresolvers import reverse
from django.conf import settings

from event_logs.models import EventLog
from perms.object_perms import ObjectPermission
from models import Testimonial
from forms import TestimonialForm


class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['view_on_site', 'first_last_name', 'testimonial_parsed', 'create_dt']
    list_filter = ['last_name', 'first_name', 'create_dt']
    search_fields = ['first_name','last_name', 'testimonial']
    ordering = ('-create_dt',)
    fieldsets = (
        (None, {'fields': (
            'first_name',
            'last_name',
            'testimonial',
            'tags',
        )}),
        ('Personal Information', {'fields': (
            'city',
            'state',
            'country',
            'email',
            'company',
            'title',
            'website',
        )}),
        ('Administrative', {'fields': (
            'allow_anonymous_view','user_perms','group_perms','status','status_detail' )}),
    )
    form = TestimonialForm

    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('testimonial.view', args=[obj.pk]),
            (obj.first_name, obj.last_name),
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'

    def first_last_name(self, obj):
        return '<a href="%s">%s %s</a>' % (
            reverse('admin:testimonials_testimonial_change', args=[obj.pk]),
            obj.first_name,
            obj.last_name,
        )
    first_last_name.allow_tags = True
    first_last_name.short_description = 'name'
    
    def testimonial_parsed(self, obj):
        testimonial = strip_tags(obj.testimonial)
        testimonial = truncate_words(testimonial, 50)
        return testimonial
    testimonial_parsed.short_description = 'testimonial'


    def log_deletion(self, request, object, object_repr):
        super(TestimonialAdmin, self).log_deletion(request, object, object_repr)
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
        super(TestimonialAdmin, self).log_change(request, object, message)
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
        super(TestimonialAdmin, self).log_addition(request, object)
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
		result = super(TestimonialAdmin, self).change_view(request, object_id, extra_context)

		if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
			result['Location'] = iri_to_uri("%s") % request.GET.get('next')
		return result

admin.site.register(Testimonial, TestimonialAdmin)
