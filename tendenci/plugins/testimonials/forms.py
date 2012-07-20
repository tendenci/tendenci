from django import forms

from perms.forms import TendenciBaseForm
from models import Testimonial

class TestimonialForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(choices=(('active','Active'),('inactive','Inactive')))

    class Meta:
        model = Testimonial
        fields = (
            'first_name',
            'last_name',
            'testimonial',
            'tags',
            'city',
            'state',
            'country',
            'email',
            'company',
            'title',
            'website',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'member_perms',
            'status',
            'status_detail',
        )