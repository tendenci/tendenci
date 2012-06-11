from django.contrib import admin
from django.utils.text import truncate_words
from django.utils.html import strip_tags
from django.conf import settings

from perms.admin import TendenciBaseModelAdmin
from models import Testimonial
from forms import TestimonialForm


class TestimonialAdmin(TendenciBaseModelAdmin):
    list_display = ['first_last_name', 'testimonial_parsed', 'create_dt']
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
    form = TestimonialForm

    def first_last_name(self, obj):
        return '%s %s' % (obj.first_name, obj.last_name)
    first_last_name.short_description = 'name'
    
    def testimonial_parsed(self, obj):
        testimonial = strip_tags(obj.testimonial)
        testimonial = truncate_words(testimonial, 50)
        return testimonial
    testimonial_parsed.short_description = 'testimonial'

admin.site.register(Testimonial, TestimonialAdmin)
