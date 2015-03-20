from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend

class NewsletterEmailBackend(EmailBackend):
    """
    A wrapper that manages the SMTP network connection for newsletters.
    """
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, **kwargs):
        kwargs.update({'host': settings.NEWSLETTER_EMAIL_HOST,
                       'port': settings.NEWSLETTER_EMAIL_PORT,
                       'username': settings.NEWSLETTER_EMAIL_HOST_USER,
                       'password': settings.NEWSLETTER_EMAIL_HOST_PASSWORD,
                       'use_tls': settings.NEWSLETTER_EMAIL_USE_TLS,
                       'fail_silently': fail_silently})
        
        super(NewsletterEmailBackend, self).__init__(**kwargs)
