

def send_registration_activation_email(user, registration_profile, **kwargs):
    """
        this function sends the activation email to the self registrant.
        modified based on the block in create_inactive_user in registration/models.py
    """
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.conf import settings
    from site_settings.utils import get_setting
    
    site_url = get_setting('site', 'global', 'siteurl')
    subject = render_to_string('registration/activation_email_subject.txt',
                                       { 'site_url': site_url })
    
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    message = render_to_string('registration/activation_email.txt',
                               { 'activation_key': registration_profile.activation_key,
                                 'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                 'site_url': site_url })
    
    from_email = get_setting('site', 'global', 'siteemailnoreplyaddress')
    
    send_mail(subject, message, from_email, [user.email])