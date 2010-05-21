from django.forms import ModelForm
from stories.models import Story

class StoryForm(ModelForm):
    class Meta:
        model = Story
        exclude = ('guid',)
        fields = (
        'title',
        'content',
        'fullstorylink',
        'start_dt',
        'end_dt',
        'ncsortorder',

        'syndicate',
        'owner',
        'status',
        'status_detail',
        )
