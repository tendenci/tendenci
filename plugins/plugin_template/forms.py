from django import forms

from S_P_LOW.models import S_S_CAP
from perms.forms import TendenciBaseForm

class S_S_CAPForm(TendenciBaseForm):

    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    
    class Meta:
        model = S_S_CAP