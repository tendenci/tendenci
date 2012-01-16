from django import forms

from tinymce.widgets import TinyMCE
from perms.forms import TendenciBaseForm
from base.fields import SplitDateTimeField

from lots.models import Lot

class LotForm(TendenciBaseForm):
    class Meta:
        model = Lot
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
