# python
import os
import codecs
from urllib.request import urlopen

# django
from django import forms
from django.core.files import File
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache

# local
from tendenci.apps.theme.utils import theme_choices
from tendenci.apps.theme_editor.utils import archive_file
from tendenci.libs.boto_s3.utils import save_file_to_s3

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
    '.woff2',
    '.svg',
)


class FileForm(forms.Form):
    content = forms.CharField(label="Content",
                           widget=forms.Textarea(attrs={'rows': 26, 'cols': 73}),
                           max_length=500000
                           )

    def save(self, root_dir, theme, file_relative_path, request):
        content = self.cleaned_data["content"]
        file_path = os.path.join(root_dir, file_relative_path)

        # write the theme file locally in case it was wiped by a restart
        if settings.USE_S3_THEME and not os.path.isfile(file_path):
            file_dir = os.path.dirname(file_path)
            if not os.path.isdir(file_dir):
                # if directory does not exist, create it
                os.makedirs(file_dir)
            new_file = open(file_path, 'w')
            new_file.write('')
            new_file.close()

        if os.path.isfile(file_path) and content != '':
            archive_file(root_dir, file_relative_path, request)

            # Save the file locally no matter the theme location.
            # The save to S3 reads from the local file, so we need to save it first.
            f = codecs.open(file_path, 'w', 'utf-8', 'replace')
            file = File(f)
            file.write(content)
            file.close()

            if settings.USE_S3_THEME:
                # copy to s3 storage
                if os.path.splitext(file_relative_path)[1] == '.html':
                    public = False
                else:
                    public = True
                dest_path = os.path.join(theme, file_relative_path)
                dest_full_path = os.path.join(settings.THEME_S3_PATH, dest_path)
                save_file_to_s3(file_path, dest_path=dest_full_path, public=public)

                cache_key = '.'.join([settings.SITE_CACHE_KEY, 'theme', dest_path])
                cache.delete(cache_key)

                if hasattr(settings, 'REMOTE_DEPLOY_URL') and settings.REMOTE_DEPLOY_URL:
                    urlopen(settings.REMOTE_DEPLOY_URL)

            return True
        else:
            return False


class ThemeNameForm(forms.Form):
    theme_name = forms.RegexField(label=_("New theme name"),
                                  regex=r'^[a-z][0-9a-z_-]+$',
                                  max_length=64)


class AddTemplateForm(forms.Form):
    template_name = forms.RegexField(label=_("Template Name"),
                                     regex=r'^[a-z][0-9a-z_-]+$',
                                     max_length=16)


class ThemeSelectForm(forms.Form):
    theme_edit = forms.ChoiceField(label=_('Theme:'), choices=[],
        widget=forms.Select(attrs={'onchange': 'submit();'}))

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
