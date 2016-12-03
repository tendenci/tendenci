# python
import os
import codecs
import urllib

# django
from django import forms
from django.core.files import File
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache

# local
from tendenci.apps.theme.utils import get_theme_root, get_theme, theme_choices
from tendenci.apps.theme_editor.utils import archive_file
from tendenci.libs.boto_s3.utils import save_file_to_s3

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
    '.gif',
    '.txt',
    '.xml',
    '.kml',
    '.eot',
    '.ttf',
    '.woff',
    '.svg',
)


class FileForm(forms.Form):
    content = forms.CharField(label="Content",
                           widget=forms.Textarea(attrs={'rows': 26, 'cols': 73}),
                           max_length=500000
                           )
    rf_path = forms.CharField(widget=forms.HiddenInput())

    def save(self, request, file_relative_path, ROOT_DIR=THEME_ROOT, ORIG_ROOT_DIR=THEME_ROOT):
        content = self.cleaned_data["content"]
        file_path = (os.path.join(ROOT_DIR, file_relative_path)).replace("\\", "/")

        if settings.USE_S3_THEME:
            file_path = (os.path.join(ORIG_ROOT_DIR, file_relative_path)).replace("\\", "/")

        # write the theme file locally in case it was wiped by a restart
        if settings.USE_S3_THEME and not os.path.isfile(file_path):
            file_dir = os.path.dirname(file_path)
            if not os.path.isdir(file_dir):
                # if directory does not exist, create it
                os.makedirs(file_dir)
            new_file = open(file_path, 'w')
            new_file.write('')
            new_file.close()

        if os.path.isfile(file_path) and content != "":
            archive_file(request, file_relative_path, ROOT_DIR=ORIG_ROOT_DIR)

            # Save the file locally no matter the theme location.
            # The save to S3 reads from the local file, so we need to save it first.
            f = codecs.open(file_path, 'w', 'utf-8', 'replace')
            file = File(f)
            file.write(content)
            file.close()

            if settings.USE_S3_THEME:
                # copy to s3 storage
                if os.path.splitext(file_path)[1] == '.html':
                    public = False
                else:
                    public = True
                save_file_to_s3(file_path, public=public)

                cache_key = ".".join([settings.SITE_CACHE_KEY, 'theme', "%s/%s" % (get_theme(), file_relative_path)])
                cache.delete(cache_key)

                if hasattr(settings, 'REMOTE_DEPLOY_URL') and settings.REMOTE_DEPLOY_URL:
                    urllib.urlopen(settings.REMOTE_DEPLOY_URL)

            return True
        else:
            return False


class AddTemplateForm(forms.Form):
    template_name = forms.RegexField(label=_("Template Name"),
                                     regex=r'^[a-z][0-9a-z_-]+$',
                                     max_length=20)


class ThemeSelectForm(forms.Form):
    theme_edit = forms.ChoiceField(label=_('Theme:'), choices=[])

    def __init__(self, *args, **kwargs):
        super(ThemeSelectForm, self).__init__(*args, **kwargs)
        THEME_CHOICES = ((x, x) for x in theme_choices())
        self.fields['theme_edit'].choices = THEME_CHOICES


class UploadForm(forms.Form):
    qqfilename = forms.CharField()
    file_dir = forms.CharField(widget=forms.HiddenInput, required=False)
    overwrite = forms.BooleanField(widget=forms.HiddenInput, required=False)

    def clean_qqfilename(self):
        data = self.cleaned_data['qqfilename']
        if not data.lower().endswith(FILE_EXTENTIONS):
            raise forms.ValidationError(_("This is not a valid file type to upload."))
        return data
