from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.conf import settings

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import update_perms_and_save
from tendenci.apps.projects.models import (
    Project,
    ProjectManager,
    ProjectNumber,
    Photo,
    DocumentType,
    ClientList,
    TeamMembers,
    Documents,
    Category,
    CategoryPhoto)

from tendenci.apps.projects.forms import ProjectForm, PhotoForm, DocumentsForm, TeamMembersForm, CategoryAdminForm


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image_preview', 'position',)
    list_display_links = ('name',)
    list_editable = ('position',)
    fieldsets = (
        (None, {
            'fields': ('name', 'photo_upload', 'position',)
        },),)
    form = CategoryAdminForm
    order = ['position']

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.11.0/jquery-ui.min.js',
            '%sjs/admin/staff-dynamic-sort.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }

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

    def save_model(self, request, object, form, change):
        super(CategoryAdmin, self).save_model(request, object, form, change)

        category_photo = CategoryPhoto()
        image = form.cleaned_data.get('photo_upload')

        if image:
            category_photo.file = image
            category_photo.save()
            object.image = category_photo
            object.save()


class PhotoAdmin(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': (
            'title',
            'photo_description',
            'file',
        )},),
    )
    model = Photo
    form = PhotoForm

class TeamMembersAdmin(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': (
            'first_name',
            'last_name',
            'title',
            'role',
            'team_description',
            'file',
        )},),
    )
    model = TeamMembers
    form = TeamMembersForm

class DocumentsAdmin(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': (
            'type',
            'other',
            'document_dt',
            'file',
        )},),
    )
    model = Documents
    form = DocumentsForm

class ProjectAdmin(TendenciBaseModelAdmin):
    list_display = [u'project_name', 'view_on_site', 'edit_link', 'tags']
    list_filter = []
    search_fields = []
    actions = []
    inlines = (PhotoAdmin, TeamMembersAdmin, DocumentsAdmin,)
    prepopulated_fields = {'slug': ['project_name']}
    
    form = ProjectForm
    
    fieldsets = (
        (None, 
            {'fields': (
                'project_name',
                'slug',
                'project_number',
                'project_status',
                'category',
                'cost',
                'location',
                'city',
                'state',
                'project_manager',
                'project_description',
                'video_title',
                'video_description',
                'video_embed_code',
                'start_dt',
                'end_dt',
                'resolution',
                'client',
                'website_url',
                'website_title',
                'tags'
            )}
        ),
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
        )


    def save_formset(self, request, form, formset, change):
        for f in formset.forms:
            if f.changed_data:
                file = f.save(commit=False)
                if file.file:
                    file.project = form.save()
                    file.content_type = ContentType.objects.get_for_model(file.project)
                    file.object_id = file.project.pk
                    file.name = file.file.name
                    file.creator = request.user
                    file.owner = request.user
                    file.save()

        formset.save()

    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:projects_project_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'

    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('projects.detail', args=[obj.slug]),
            obj,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'

    # def log_deletion(self, request, object, object_repr):
    #     super(ProjectAdmin, self).log_deletion(request, object, object_repr)
    #     log_defaults = {
    #         'event_id' : 1180300,
    #         'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
    #                                                 object.pk, request.user),
    #         'description': '%s deleted' % object._meta.object_name,
    #         'user': request.user,
    #         'request': request,
    #         'instance': object,
    #     }
    #     EventLog.objects.log(**log_defaults)           

    # def log_change(self, request, object, message):
    #     super(ProjectAdmin, self).log_change(request, object, message)
    #     log_defaults = {
    #         'event_id' : 1180200,
    #         'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
    #                                                 object.pk, request.user),
    #         'description': '%s edited' % object._meta.object_name,
    #         'user': request.user,
    #         'request': request,
    #         'instance': object,
    #     }
    #     EventLog.objects.log(**log_defaults)               

    # def log_addition(self, request, object):
    #     super(ProjectAdmin, self).log_addition(request, object)
    #     log_defaults = {
    #         'event_id' : 1180100,
    #         'event_data': '%s (%d) added by %s' % (object._meta.object_name, 
    #                                                object.pk, request.user),
    #         'description': '%s added' % object._meta.object_name,
    #         'user': request.user,
    #         'request': request,
    #         'instance': object,
    #     }
    #     EventLog.objects.log(**log_defaults)
                     
    # def get_form(self, request, obj=None, **kwargs):
    #     """
    #     inject the user in the form.
    #     """
    #     form = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
    #     form.current_user = request.user
    #     return form

    # def save_model(self, request, object, form, change):
    #     """
    #     update the permissions backend
    #     """
    #     instance = form.save(commit=False)
    #     perms = update_perms_and_save(request, form, instance)
    #     return instance

    # def change_view(self, request, object_id, extra_context=None):
    #     result = super(ProjectAdmin, self).change_view(request, object_id, extra_context)
    #     if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
    #         result['Location'] = iri_to_uri("%s") % request.GET.get('next')
    #     return result

admin.site.register(ProjectNumber)
admin.site.register(ProjectManager)
admin.site.register(ClientList)
admin.site.register(DocumentType)
admin.site.register(Category, CategoryAdmin)
# admin.site.register(PhotoAdmin)
# admin.site.register(TeamMembersAdmin)
# admin.site.register(DocumentsAdmin)
admin.site.register(Project, ProjectAdmin)
