from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

@deconstructible
class UnicodeNameValidator(validators.RegexValidator):
    regex = r'^[\w\s.+-]+$'
    message = _(
        'Enter a valid value. This value may contain only letters, '
        'numbers, spaces and @/./+/-/_ characters.'
    )
    flags = 0
