from django import forms

from museums.models import Museum
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class MuseumForm(TendenciBaseForm):
    class Meta:
        model = Museum
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
