from django import forms
from tendenci.apps.profiles.models import Profile
from tendenci.core.api_tasty.forms import TendenciForm

class ProfileForm(TendenciForm):
    """Profile Form
    """
    class Meta:
        model = Profile
        exclude = ("guid", )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
