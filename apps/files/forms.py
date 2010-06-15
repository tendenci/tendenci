from django import forms
from files.models import File

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = (
        'file',
        )

    def __init__(self, user=None, *args, **kwargs): 
        self.user = user
        super(FileForm, self).__init__(*args, **kwargs)