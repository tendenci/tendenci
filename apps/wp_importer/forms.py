from django import forms
from django.forms import ModelForm
from django.conf import settings
from django.utils.translation import gettext as _
from wp_importer.models import BlogImport

class BlogImportForm(forms.ModelForm):
    blog = forms.Field(widget=forms.FileInput, required=True)
    # print blog_file

    class Meta():
        model = BlogImport
        fields = ('blog',)