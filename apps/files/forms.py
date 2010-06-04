from django import forms
from files.models import File

class FileAddForm(forms.ModelForm):
    class Meta:
        model = File
        fields = (
        'file',
        )

class FileEditForm(forms.ModelForm):
    class Meta:
        model = File
        fields = (
        'file',
        )