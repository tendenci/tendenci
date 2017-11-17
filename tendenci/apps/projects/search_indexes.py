from haystack import indexes

from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.projects.models import Project


class ProjectIndex(TendenciBaseSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    slug = indexes.CharField(model_attr='slug')
    project_name = indexes.CharField(model_attr='project_name')
    project_status = indexes.CharField(model_attr='project_status',)
    location = indexes.CharField(model_attr='location',)
    city = indexes.CharField(model_attr='city',)
    state = indexes.CharField(model_attr='state',)
    start_dt = indexes.DateTimeField(model_attr='start_dt', null=True)
    end_dt = indexes.DateTimeField(model_attr='end_dt', null=True)
    website_title = indexes.CharField(model_attr='website_title',)
    website_url = indexes.CharField(model_attr='website_url',)
    video_embed_code = indexes.CharField(model_attr='video_embed_code',)
    video_title = indexes.CharField(model_attr='video_title',)
    video_description = indexes.CharField(model_attr='video_description',)

    @classmethod
    def get_model(self):
        return Project
