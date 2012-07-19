from django.template import Context
from django.template.loader import get_template
from site_settings.utils import get_setting

def get_vcard_content(attorney):
    """
    Create the content of the vcard
    """
    context = Context()
    template = get_template('attorneys/vcard.html')
    site_name = get_setting('site', 'global', 'sitedisplayname')

    context['attorney'] = attorney
    context['SITE_GLOBAL_SITEDISPLAYNAME'] = site_name
    output = template.render(context)

    return output
