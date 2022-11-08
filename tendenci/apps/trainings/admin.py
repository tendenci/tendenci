from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import SchoolCategory, Certification, CertCat, Course
from .forms import CourseForm


class SchoolCategoryAdmin(admin.ModelAdmin):
    model = SchoolCategory
    list_display = ['id', 'name',
                    'status_detail',]


class CategoryAdminInline(admin.TabularInline):
    fieldsets = (
        (None, {
            'fields': (
            'category',
            'required_credits'
        )},),
    )
    extra = 0
    model = CertCat


class CertificationAdmin(admin.ModelAdmin):
    model = SchoolCategory
    list_display = ['id', 'name',
                    'period',]
    inlines = (CategoryAdminInline,)


class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = ['id', 'name',
                    'location_type',
                    'school_category',
                    'status_detail'
                    ]
    search_fields = ['name', 'location_type']
    list_filter = ['status_detail', 'location_type', 'school_category']
    fieldsets = (
        (_('General'), {
            'fields': ('name',
                       'location_type',
                       'school_category',
                       'course_code',
                       'summary',
                       'description',
                       'credits',
                       'min_score',
                       'status_detail',)
        }),
        (_('Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        )
    form = CourseForm


admin.site.register(SchoolCategory, SchoolCategoryAdmin)
admin.site.register(Certification, CertificationAdmin)
admin.site.register(Course, CourseAdmin)
