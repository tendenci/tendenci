from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.staff.models import Staff, Position, Department, StaffFile
from tendenci.apps.staff.forms import StaffForm, FileForm


class FileAdmin(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': (
            'file',
            'photo_type',
            'description',
            'position',
        )},),
    )
    model = StaffFile
    form = FileForm
    extra = 0


class StaffAdmin(TendenciBaseModelAdmin):
    list_display = ['name', 'slug', 'department', 'phone', 'position']
    list_filter = ['department']
    list_editable = ['position']
    search_fields = ['name', 'biography', 'cv']
    prepopulated_fields = {'slug': ['name']}
    fieldsets = (
        (None, {'fields': (
            'name',
            'slug',
            'department',
            'positions',
            'biography',
            'cv',
            'email',
            'phone',
            'personal_sites',
            'tags'
        )}),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'status_detail',
        )}),
    )
    form = StaffForm
    ordering = ['-position']
    inlines = (FileAdmin,)

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.11.0/jquery-ui.min.js',
            '%sjs/admin/staff-dynamic-sort.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }

    def years(self, obj):
        return obj.years()

    def save_formset(self, request, form, formset, change):
        for f in formset.forms:
            file = f.save(commit=False)
            if file.file:
                file.staff = form.save()
                file.content_type = ContentType.objects.get_for_model(file.staff)
                file.object_id = file.staff.pk
                file.name = file.file.name
                file.creator = request.user
                file.owner = request.user
                file.save()

        formset.save()


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

admin.site.register(Staff, StaffAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Position)
