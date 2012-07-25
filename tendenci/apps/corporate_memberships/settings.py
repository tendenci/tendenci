from django.conf import settings
from tendenci.apps.site_settings.utils import get_setting


# Maximum allowed length for field values.
FIELD_MAX_LENGTH = getattr(settings, "FORMS_BUILDER_FIELD_MAX_LENGTH", 2000)

# Maximum allowed length for field labels.
LABEL_MAX_LENGTH = getattr(settings, "FORMS_BUILDER_LABEL_MAX_LENGTH", 255)

# Absolute path where files will be uploaded to.
UPLOAD_ROOT = getattr(settings, "MEDIA_ROOT", None)

use_search_index = get_setting('site', 'global', 'searchindex')
if use_search_index in ('true', True):
    use_search_index = True
else:
    use_search_index = False
