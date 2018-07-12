"""
from tendenci.apps.newsletters.models import Newsletter


class NewsletterRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Create newsletter')

    event_logs = {
        'newsletter':{
            'add': ('136000','DD3300'),
            'edit': ('136100', 'DD3311'),
            'detail': ('136200', 'DD3322'),
            'send': ('136300', 'DD3333'),
            'resend': ('136400', 'DD3344')
        }
    }
    url = {
        'add': lazy_reverse('newsletter.orig.generator'),
        'search': lazy_reverse('newsletter.list'),
    }

site.register(Newsletter, NewsletterRegistry)
"""
