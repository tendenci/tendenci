from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import iri_to_uri
from django.utils.text import truncate_words
from django.utils.html import strip_tags
from django.core.urlresolvers import reverse
from django.conf import settings

from event_logs.models import EventLog
from perms.object_perms import ObjectPermission
from models import ArchitectureProject, Category, BuildingType, Image
from forms import ArchitectureProjectForm, FileForm

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

class ArchitectureProjectAdmin(admin.ModelAdmin):
    list_display = ['view_on_site', 'edit_link', 'client', 'project_title', 'slug', 'overview_parsed', 'create_dt']
    list_filter = ['create_dt']
    search_fields = ['client','overview', 'execution', 'results']
    ordering = ('-create_dt',)
    prepopulated_fields = {'slug': ['client']}
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

    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/architecture-projects-dynamic-sort.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }

    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:architecture_projects_architectureproject_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'
    
    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('architecture_project.view', args=[obj.slug]),
            obj.client,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'

    def overview_parsed(self, obj):
        overview = strip_tags(obj.overview)
        overview = truncate_words(overview, 50)
        return overview
    overview_parsed.short_description = 'overview'


    def log_deletion(self, request, object, object_repr):
        super(ArchitectureProjectAdmin, self).log_deletion(request, object, object_repr)
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
        super(ArchitectureProjectAdmin, self).log_change(request, object, message)
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
        super(ArchitectureProjectAdmin, self).log_addition(request, object)
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
        add = not change

        # set up user permission
        instance.allow_user_view, instance.allow_user_edit = form.cleaned_data['user_perms']

        if add:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username

        # save the object
        instance.save()
        form.save_m2m()

        # permissions
        if add:
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
                image.save()

        formset.save()


    def change_view(self, request, object_id, extra_context=None):
        result = super(ArchitectureProjectAdmin, self).change_view(request, object_id, extra_context)

        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

admin.site.register(ArchitectureProject, ArchitectureProjectAdmin)
admin.site.register(Category)
admin.site.register(BuildingType)
admin.site.register(Image)
