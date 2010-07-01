from django import forms
from datetime import datetime
from django.utils.translation import ugettext_lazy as _

from media_files.models import MediaFile

class MediaFileForm(forms.ModelForm):
    
    class Meta:
        model = MediaFile