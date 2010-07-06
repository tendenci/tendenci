from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from stories.models import Story
from perms.forms import TendenciBaseForm
from base.fields import SplitDateTimeField

class StoryForm(TendenciBaseForm):
    fullstorylink = forms.CharField(label=_("Full Story Link"), required=False, max_length=300)

    start_dt = SplitDateTimeField(label=_('Start Date/Time'),
                                    initial=datetime.now())

    end_dt = SplitDateTimeField(label=_('End Date/Time'),
                                    initial=datetime.now())
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
      
class UploadStoryImageForm(forms.Form):
    file  = forms.FileField(label=_("File Path"))


