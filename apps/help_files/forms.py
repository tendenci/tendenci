from django import forms

from models import Request, HelpFile
from tinymce.widgets import TinyMCE
from captcha.fields import CaptchaField
from perms.forms import TendenciBaseForm
   
class RequestForm(forms.ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = Request

class HelpFileForm(TendenciBaseForm):
    answer = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':HelpFile._meta.app_label, 
        'storme_model':HelpFile._meta.module_name.lower()}))

    status_detail = forms.ChoiceField(choices=(('draft','Draft'),('published','Published')))
    
    class Meta:
        model = HelpFile

    def __init__(self, *args, **kwargs): 
        super(HelpFileForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['answer'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['answer'].widget.mce_attrs['app_instance_id'] = 0