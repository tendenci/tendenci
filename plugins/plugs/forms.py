from django import forms

from plugs.models import Plug
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class PlugForm(TendenciBaseForm):
    class Meta:
        model = Plug
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    brother = forms.CharField(required=False,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'plugs','storme_model':Plug._meta.module_name.lower()}))
