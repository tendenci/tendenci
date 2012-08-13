from django import forms
from django.forms import ModelForm
from django.conf import settings
from django.utils.translation import gettext as _
from tendenci.apps.wp_importer.models import BlogImport

class BlogImportForm(forms.ModelForm):
    blog = forms.Field(widget=forms.FileInput, required=True)

    class Meta():
        model = BlogImport
        fields = ('blog',)