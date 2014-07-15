

def send_registration_activation_email(user, registration_profile, **kwargs):
    """
        this function sends the activation email to the self registrant.
        modified based on the block in create_inactive_user in registration/models.py
    """
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.conf import settings
    from tendenci.core.site_settings.utils import get_setting

    event = kwargs.pop('event', None)
    event_url = None
    if event: event_url = event.get_absolute_url()

    site_url = get_setting('site', 'global', 'siteurl')
    subject = render_to_string('registration/activation_email_subject.txt',
                                       { 'site_url': site_url })

    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    message = render_to_string('registration/activation_email.txt',
                               { 'activation_key': registration_profile.activation_key,
                                 'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                 'event_url': event_url,
                                 'site_url': site_url })

    from_email = get_setting('site', 'global', 'siteemailnoreplyaddress') or settings.DEFAULT_FROM_EMAIL

    send_mail(subject, message, from_email, [user.email])
