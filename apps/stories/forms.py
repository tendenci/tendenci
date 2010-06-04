from stories.models import Story
from perms.forms import AuditingBaseForm

class StoryForm(AuditingBaseForm):
    class Meta:
        model = Story
        fields = (
        'title',
        'content',
        'fullstorylink',
        'start_dt',
        'end_dt',
        'ncsortorder',
        'syndicate',
        'status',
        'status_detail',
        )
      
    def __init__(self, user=None, *args, **kwargs): 
        self.user = user
        super(StoryForm, self).__init__(user, *args, **kwargs)
