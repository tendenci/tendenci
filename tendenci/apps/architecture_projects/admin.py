from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.text import truncate_words
from django.utils.html import strip_tags
from django.conf import settings

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.architecture_projects.models import ArchitectureProject, Category, BuildingType, Image
from tendenci.apps.architecture_projects.forms import ArchitectureProjectForm, FileForm

class FileAdmin(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': (
            'file',
            'file_type',
            'description',
            'position',
        )},),
    )
    model = Image
    form = FileForm
    extra = 0

class ArchitectureProjectAdmin(TendenciBaseModelAdmin):
    list_display = ['client', 'project_title', 'status', 'ordering']
    list_filter = ['client']
    search_fields = ['client','overview', 'execution', 'results', 'architect', 'project_title']
    ordering = ('-create_dt',)
    list_editable = ['ordering', 'status']
    prepopulated_fields = {'slug': ['project_title']}
    fieldsets = (
        (None, {'fields': (
            'architect',
            'project_title',
            'client',
            'slug',
            'url',
            'overview',
            'execution',
            'categories',
            'building_types',
            'results',
            'tags'
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
    form = ArchitectureProjectForm
    inlines = (FileAdmin,)
    ordering = ['-ordering']

    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }

    def overview_parsed(self, obj):
        overview = strip_tags(obj.overview)
        overview = truncate_words(overview, 50)
        return overview
    overview_parsed.short_description = 'overview'

    def save_formset(self, request, form, formset, change):

        for f in formset.forms:
            image = f.save(commit=False)
            if image.file:
                image.architecture_project = form.save()
                image.content_type = ContentType.objects.get_for_model(image.architecture_project)
                image.object_id = image.architecture_project.pk
                image.name = image.file.name
                image.creator = request.user
                image.owner = request.user
                image.save(log=False)

        formset.save()

admin.site.register(ArchitectureProject, ArchitectureProjectAdmin)
admin.site.register(Category)
admin.site.register(BuildingType)
admin.site.register(Image)
