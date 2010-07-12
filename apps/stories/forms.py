from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from stories.models import Story
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class StoryForm(TendenciBaseForm):
    STATUS_CHOICES = (('active','Active'),('inactive','Inactive'), ('pending','Pending'),)

    content = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Story._meta.app_label, 
        'storme_model':Story._meta.module_name.lower()}))

    fullstorylink = forms.CharField(label=_("Full Story Link"), required=False, max_length=300)

    start_dt = SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now())

    end_dt = SplitDateTimeField(label=_('End Date/Time'), initial=datetime.now())

    status_detail = forms.ChoiceField(choices=STATUS_CHOICES)

    class Meta:
        model = Story
        fields = (
        'title',
        'content',
        'fullstorylink',
        'start_dt',
        'end_dt',
        'syndicate',
        'status',
        'status_detail',
        )
      
    def __init__(self, user=None, *args, **kwargs):
        super(StoryForm, self).__init__(user, *args, **kwargs)
        self.user = user
        self.fields['user_perms'].label = "Owner"
        self.fields['user_perms'].help_text = "Non-admin who can edit this story"
        if self.instance.pk:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = 0
      
class UploadStoryImageForm(forms.Form):
    file  = forms.FileField(label=_("File Path"))


