# python
import os
import codecs

# django
from django import forms
from django.core.files import File
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# local
from theme.utils import get_theme_root, get_theme, theme_choices
from theme_editor.utils import archive_file

THEME_ROOT = get_theme_root()
FILE_EXTENTIONS = (
    '.html',
    '.js',
    '.css',
    '.less',
    '.jpg',
    '.jpeg',
    '.png',
    '.ico',
    '.gif'
)

class FileForm(forms.Form):
    content = forms.CharField(label="Content",
                           widget=forms.Textarea(attrs={'rows':26, 'cols':73}),
                           max_length=500000
                           )
    rf_path = forms.CharField(widget=forms.HiddenInput())
    
    def save(self, request, file_relative_path, ROOT_DIR=THEME_ROOT):
        content = self.cleaned_data["content"]
        file_path = (os.path.join(ROOT_DIR, file_relative_path)).replace("\\", "/")
        if os.path.isfile(file_path) and content <> "":
            archive_file(request, file_relative_path, ROOT_DIR=ROOT_DIR)
            f = codecs.open(file_path, 'w', 'utf-8', 'replace')
            file = File(f)
            file.write(content)
            file.close()
            return True
        else:
            return False
            
class ThemeSelectForm(forms.Form):
    THEME_CHOICES = ((x, x) for x in theme_choices())
    theme_edit = forms.ChoiceField(label = _('Theme:'), choices=THEME_CHOICES)
    
    def __init__(self, *args, **kwargs):
        super(ThemeSelectForm, self).__init__(*args, **kwargs)
    
class UploadForm(forms.Form):
    upload = forms.FileField()
    file_dir = forms.CharField(widget=forms.HiddenInput, required=False)
    overwrite = forms.BooleanField(widget=forms.HiddenInput, required=False)
    
    def clean_file_dir(self):
        data = self.cleaned_data['file_dir']
        if data:
            data = data.replace('\\','/')
            data = data.strip('/')
            data = data.replace('////', '/')
            data = data.replace('///', '/')
            data = data.replace('//', '/')
        else:
            data ="templates"
        return data
    
    def clean_upload(self):
        data = self.cleaned_data['upload']
        if not data.name.endswith(FILE_EXTENTIONS):
            raise forms.ValidationError("This is not a valid file type to upload.")
        return data
        
