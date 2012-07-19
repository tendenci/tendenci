from haystack import indexes
from haystack import site

from perms.indexes import TendenciBaseSearchIndex
from chamberlin_projects.models import Project

class ProjectIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title',)
    slug = indexes.CharField(model_attr='slug',)
    location = indexes.CharField(model_attr='location', null=True,)
    city = indexes.CharField(model_attr='city', null=True,)
    state = indexes.CharField(model_attr='state', null=True,)
    contract_amount = indexes.IntegerField(model_attr='contract_amount', null=True,)
    owner = indexes.CharField(model_attr='owner', null=True,)
    architect = indexes.CharField(model_attr='architect', null=True,)
    general_contractor = indexes.CharField(model_attr='general_contractor', null=True,)
    scope_of_work = indexes.CharField(model_attr='scope_of_work', null=True,)
    project_description = indexes.CharField(model_attr='project_description', null=True,)

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_syndicate_order(self, obj):
        return obj.update_dt

site.register(Project, ProjectIndex)
