from django import forms
from profiles.models import Profile
from api_tasty.forms import TendenciForm

class ProfileForm(TendenciForm):
    """Profile Form
    """
    class Meta:
        model = Profile
        
