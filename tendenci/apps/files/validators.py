# Updated based on the gist https://gist.github.com/jrosebr1/2140738
# This updated version uses python-magic to detect the mimetype from the content of a file instead of the file extension.

import magic
from os.path import splitext

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import filesizeformat
from tendenci.apps.files.utils import get_max_file_upload_size, get_allowed_upload_file_exts, get_allowed_mimetypes


class FileValidator(object):
    """
    Validator for files, checking the size, extension and mimetype.

    Initialization parameters:
        allowed_extensions: iterable with allowed file extensions
            ie. ('.txt', '.doc')
        allowd_mimetypes: iterable with allowed mimetypes
            ie. ('image/png', )
        min_size: minimum number of bytes allowed
            ie. 100
        max_size: maximum number of bytes allowed
            ie. 24*1024*1024 for 24 MB

    Usage example:

        file = forms.FileField(validators=[FileValidator(allowed_extensions=('.pdf', '.doc',))], ...)

    """

    extension_message = _("Extension '%(extension)s' not allowed. Allowed extensions are: '%(allowed_extensions)s.'")
    mime_message = _("MIME type '%(mimetype)s' is not valid. Allowed types are: %(allowed_mimetypes)s.")
    max_size_message = _('The current file %(size)s, which is too large. The maximum file size is %(allowed_size)s.')

    def __init__(self, *args, **kwargs):
        self.allowed_extensions = kwargs.pop('allowed_extensions', get_allowed_upload_file_exts())
        self.allowed_mimetypes = kwargs.pop('allowed_mimetypes', get_allowed_mimetypes(self.allowed_extensions))
        self.max_size = kwargs.pop('max_size', get_max_file_upload_size(file_module=True))

    def __call__(self, values):
        """
        Check the extension, content type and file size.
        """

        if not isinstance(values, list):
            values = [values]

        for value in values:
            # Block file names with a comma or two consecutive dots in it
            if ',' in value.name:
                raise ValidationError(_("Invalid file name - comma is not allowed."))
            if '..' in value.name:
                raise ValidationError(_("Invalid file name - two consecutive dots are not allowed."))
            if len(value.name) > 100:
                # The max_length (260) is set way too high in the File model, while Memcached does not accept keys longer than 250. 
                # Instead of changing the max_length in model, set limit here so that it does not break the existing db
                raise ValidationError(_("Invalid file name - the length of file name should be shorter than 100."))
            
            # Check the extension
            ext = splitext(value.name)[1].lower()
            if self.allowed_extensions and ext not in self.allowed_extensions:
                message = self.extension_message % {
                    'extension' : ext,
                    'allowed_extensions': ', '.join(self.allowed_extensions)
                }

                raise ValidationError(message)

            # Check the content type
            try:
                mime_type = magic.from_buffer(value.read(1024), mime=True)
                if self.allowed_mimetypes and mime_type not in self.allowed_mimetypes:
                    message = self.mime_message % {
                        'mimetype': mime_type,
                        'allowed_mimetypes': ', '.join(self.allowed_mimetypes)
                    }

                    raise ValidationError(message)
            except AttributeError:
                raise ValidationError(_('File type is not valid'))

            # Check the file size
            filesize = len(value)
            if self.max_size and filesize > self.max_size:
                message = self.max_size_message % {
                    'size': filesizeformat(filesize),
                    'allowed_size': filesizeformat(self.max_size)
                }

                raise ValidationError(message)
