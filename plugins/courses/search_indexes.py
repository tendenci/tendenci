from haystack import indexes
from haystack import site

from perms.indexes import TendenciBaseSearchIndex
from courses.models import Course

class CourseIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    content = indexes.CharField(model_attr='content')
    retries = indexes.IntegerField(model_attr='retries')
    retry_interval = indexes.IntegerField(model_attr='retry_interval')
    passing_score = indexes.IntegerField(model_attr='passing_score')
    deadline = indexes.DateTimeField(model_attr='deadline')

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_syndicate_order(self, obj):
        return obj.update_dt

site.register(Course, CourseIndex)
