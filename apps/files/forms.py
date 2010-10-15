from django import forms
from files.models import File

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = (
        'file',
        )

    def __init__(self, *args, **kwargs): 
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        else:
            self.user = None
        super(FileForm, self).__init__(*args, **kwargs)