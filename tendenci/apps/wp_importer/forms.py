from django import forms
from tendenci.apps.wp_importer.models import BlogImport

class BlogImportForm(forms.ModelForm):
    blog = forms.Field(widget=forms.FileInput, required=True)

    class Meta():
        model = BlogImport
        fields = ('blog',)
