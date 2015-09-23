from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from tendenci.apps.base.utils import truncate_words
from django.utils.html import strip_tags
from django.conf import settings

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.case_studies.models import CaseStudy, Image
from tendenci.apps.case_studies.forms import CaseStudyForm, FileForm


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


class CaseStudyAdmin(TendenciBaseModelAdmin):
    list_display = ['client', 'slug', 'overview_parsed', 'create_dt']
    list_filter = ['create_dt']
    search_fields = ['client', 'overview', 'execution', 'results']
    ordering = ('-create_dt',)
    prepopulated_fields = {'slug': ['client']}
    fieldsets = (
        (None, {'fields': (
            'client',
            'slug',
            'overview',
            'execution',
            'results',
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
    form = CaseStudyForm
    inlines = (FileAdmin,)

    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/case-studies-dynamic-sort.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
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
                image.case_study = form.save()
                image.content_type = ContentType.objects.get_for_model(image.case_study)
                image.object_id = image.case_study.pk
                image.name = image.file.name
                image.creator = request.user
                image.owner = request.user
                image.save(log=False)

        formset.save()

admin.site.register(CaseStudy, CaseStudyAdmin)
admin.site.register(Image)
