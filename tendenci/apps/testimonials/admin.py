from django.contrib import admin
from django.template.defaultfilters import truncatewords as truncate_words
from django.utils.html import strip_tags
from django.core.urlresolvers import reverse

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.testimonials.models import Testimonial
from tendenci.apps.testimonials.forms import TestimonialForm
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import update_perms_and_save


class TestimonialAdmin(TendenciBaseModelAdmin):
    list_display = ['image_preview', 'first_last_name', 'testimonial_parsed', 'create_dt']
    list_filter = ['last_name', 'first_name', 'create_dt']
    search_fields = ['first_name', 'last_name', 'testimonial']
    ordering = ('-create_dt',)
    fieldsets = (
        (None, {'fields': (
            'first_name',
            'last_name',
            'photo_upload',
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
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'status',
            'status_detail'
        )}),
    )
    form = TestimonialForm

    def first_last_name(self, obj):
        return '%s %s' % (obj.first_name, obj.last_name)
    first_last_name.short_description = 'name'

    def testimonial_parsed(self, obj):
        testimonial = strip_tags(obj.testimonial)
        testimonial = truncate_words(testimonial, 50)
        return testimonial
    testimonial_parsed.short_description = 'testimonial'

    def save_model(self, request, object, form, change):
        testimonial = form.save(commit=False)

        # save photo
        if 'photo_upload' in form.cleaned_data:
            photo = form.cleaned_data['photo_upload']
            if photo:
                testimonial.save(photo=photo)

        testimonial = update_perms_and_save(request, form, testimonial)

        log_defaults = {
            'instance': object,
            'action': "edit"
        }
        if not change:
            log_defaults['action'] = "add"
            EventLog.objects.log(**log_defaults)

        return object

    def image_preview(self, obj):
        if obj.image:
            args = [obj.image.pk]
            args.append("100x50")
            args.append("crop")
            return '<img src="%s" />' % reverse('file', args=args)
        else:
            return "No image"
    image_preview.allow_tags = True
    image_preview.short_description = 'Image'

admin.site.register(Testimonial, TestimonialAdmin)