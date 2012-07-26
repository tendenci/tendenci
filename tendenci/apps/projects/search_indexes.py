from haystack import indexes
from haystack import site

from tendenci.core.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.projects.models import Project

class ProjectIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title',)
    slug = indexes.CharField(model_attr='slug')
    project_name = indexes.CharField(model_attr='project_name')
    program = indexes.CharField(model_attr='program')
    program_year = indexes.CharField(model_attr='program_year')
    project_number = indexes.CharField(model_attr='project_number')
    project_status = indexes.CharField(model_attr='project_status',)
    principal_investigator = indexes.CharField(model_attr='principal_investigator',)
    principal_investigator_company = indexes.CharField(model_attr='principal_investigator_company',)
    participants = indexes.CharField(model_attr='participants',)
    rpsea_pm = indexes.CharField(model_attr='rpsea_pm',)
    start_dt = indexes.DateTimeField(model_attr='start_dt',)
    end_dt = indexes.DateTimeField(model_attr='end_dt',)
    project_abstract_date = indexes.DateTimeField(model_attr='project_abstract_date',)
    project_fact_sheet_title = indexes.CharField(model_attr='project_fact_sheet_title',)
    project_fact_sheet_url = indexes.CharField(model_attr='project_fact_sheet_url',)
    website_title = indexes.CharField(model_attr='website_title',)
    website_url = indexes.CharField(model_attr='website_url',)
    article_title = indexes.CharField(model_attr='article_title',)
    article_url = indexes.CharField(model_attr='article_url',)
    project_objectives = indexes.CharField(model_attr='project_objectives',)
    video_embed_code = indexes.CharField(model_attr='video_embed_code',)
    video_title = indexes.CharField(model_attr='video_title',)
    video_description = indexes.CharField(model_attr='video_description',)
    access_type = indexes.CharField(model_attr='access_type',)
    research_category = indexes.CharField(model_attr='research_category',)

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_syndicate_order(self, obj):
        return obj.update_dt

site.register(Project, ProjectIndex)
