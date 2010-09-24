from re import compile
from django.core.validators import RegexValidator
from django.forms.fields import CharField
from django.utils.translation import ugettext_lazy as _

slug_re = compile(r'^[-\w\/]+$')
validate_slug = RegexValidator(slug_re, _(u"Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens."), 'invalid')

class SlugField(CharField):
    """
        New form slug field that validates with front slashes
        Straight copy from django with modifications
    """
    default_error_messages = {
        'invalid': _(u"Enter a valid 'slug' consisting of letters, numbers,"
                     u" underscores (_), front-slashes (/) or hyphens."),
    }
    default_validators = [validate_slug]
    
    def __init__(self, help_text=None, *args, **kwargs):
        super(SlugField, self).__init__(*args, **kwargs)
        
    def clean(self, value):
        value = self.to_python(value)     
        value = value.replace('//','')
        value = value.strip('/')

        self.validate(value)
        self.run_validators(value)
        
        return value
        