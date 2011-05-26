from os.path import basename
from django.conf import settings
from site_settings.utils import get_setting

def generate_email_body(entry):
    """
        Generates the email body so that is readable
    """
    body = []
    body.append('<h3>%s</h3>' % entry.form.title)    
    site_url = get_setting('site', 'global', 'siteurl')
    for field in entry.fields.all():
        body.append('<p><strong>%s</strong><br />' % field.field.label)
        if field.field.field_type == 'FileField':
            url = site_url + settings.MEDIA_URL + field.value
            body.append('<em><a href="%s">%s</a></em></p>' % (url, basename(field.value)))
        else:    
            body.append('<em>%s</em></p>' % field.value)
        
    return ''.join(body)
