from tendenci.apps.events.models import Event
from tendenci.apps.api_tasty.forms import TendenciForm
from tendenci.apps.api_tasty.profiles.forms import ProfileForm

class EventForm(TendenciForm):
    """Profile Form
    """
    class Meta:
        model = Event
        exclude = ("guid", "image", "meta")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
