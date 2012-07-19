from django import forms

from perms.forms import TendenciBaseForm
from models import Testimonial

class TestimonialForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(choices=(('active','Active'),('inactive','Inactive')))

    class Meta:
        model = Testimonial