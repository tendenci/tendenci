from django import forms

from rfps.models import RFP
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class RFPForm(TendenciBaseForm):
    class Meta:
        model = RFP
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    contract_doc_description = forms.CharField(required=True,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'rfps','storme_model':RFP._meta.module_name.lower()}))
    
    def __init__(self, *args, **kwargs):
        super(RFPForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['contract_doc_description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['contract_doc_description'].widget.mce_attrs['app_instance_id'] = 0
