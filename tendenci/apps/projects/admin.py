from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.conf import settings

from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.utils import update_perms_and_save
from projects.models import Project, ProjectName, Program, ProgramYear, ProjectNumber, RpseaPm, AccessType, ResearchCategory, Presentation, Report, Article, Picture
from tendenci.apps.projects.forms import ProjectForm, PresentationForm, ReportForm, ArticleForm, PictureForm

class PresentationAdmin(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': (
            'title',
            'presentation_dt',
            'file',
        )},),
    )
    model = Presentation
    form = PresentationForm
    
class ReportAdmin(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': (
            'type',
            'other',
            'report_dt',
            'file',
        )},),
    )
    model = Report
    form = ReportForm

class ArticleAdmin(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': (
            'article_dt',
            'file',
        )},),
    )
    model = Article
    form = ArticleForm

class PictureAdmin(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': (
            'file',
        )},),
    )
    model = Picture
    form = PictureForm

class ProjectAdmin(admin.ModelAdmin):
    list_display = [u'title', 'view_on_site', 'edit_link', 'tags']
    list_filter = []
    search_fields = []
    actions = []
    inlines = (PresentationAdmin, ReportAdmin, ArticleAdmin, PictureAdmin,)
    prepopulated_fields = {'slug': ['title']}
    
    form = ProjectForm
    
    fieldsets = (
        (None, 
            {'fields': (
                'title',
                'slug',
                'project_name',
                'program',
                'program_year',
                'project_number',
                'project_status',
                'principal_investigator',
                'principal_investigator_company',
                'participants',
                'rpsea_pm',
                'start_dt',
                'end_dt',
                'project_abstract',
                'project_abstract_date',
                'project_fact_sheet_title',
                'project_fact_sheet_url',
                'website_title',
                'website_url',
                'article_title',
                'article_url',
                'project_objectives',
                'video_embed_code',
                'video_title',
                'video_description',
                'access_type',
                'research_category',
                'tags',
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
        """
        Associate the user to each instance saved.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            instance.content_type = ContentType.objects.get_for_model(instance.project)
            instance.object_id = instance.project.pk
            instance.name = instance.file.name
            instance.creator = request.user
            instance.owner = request.user
            instance.save(log=False)
    
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

    def log_deletion(self, request, object, object_repr):
        super(ProjectAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 1180300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(ProjectAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 1180200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(ProjectAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 1180100,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, 
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
                     
    def get_form(self, request, obj=None, **kwargs):
        """
        inject the user in the form.
        """
        form = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def save_model(self, request, object, form, change):
        """
        update the permissions backend
        """
        instance = form.save(commit=False)
        perms = update_perms_and_save(request, form, instance)
        return instance

    def change_view(self, request, object_id, extra_context=None):
        result = super(ProjectAdmin, self).change_view(request, object_id, extra_context)

        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

admin.site.register(ProjectName)
admin.site.register(Program)
admin.site.register(ProgramYear)
admin.site.register(ProjectNumber)
admin.site.register(RpseaPm)
admin.site.register(AccessType)
admin.site.register(ResearchCategory)
admin.site.register(Project, ProjectAdmin)
