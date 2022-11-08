from django.utils.translation import gettext_lazy as _

from tendenci.apps.perms.forms import TendenciBaseForm
from .models import Course


class CourseForm(TendenciBaseForm):
    class Meta:
        model = Course
        fields = (
            'name',
           'location_type',
           'school_category',
           'course_code',
           'summary',
           'description',
           'credits',
           'min_score',
           'status_detail',
           'user_perms',
           'member_perms',
           'group_perms',
           )
