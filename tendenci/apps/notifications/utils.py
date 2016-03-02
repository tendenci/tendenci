from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from tendenci.apps.perms.utils import get_notice_recipients
from tendenci.apps.notifications.models import send_emails

def send_notifications(scope, scope_category, name, label, extra_context=None):
    """
        a small wrapper for sending notification emails to
        recipients specified in site_settings.
    """
    recipients = get_notice_recipients(scope, scope_category, name)
    if recipients:
        send_emails(recipients, label, extra_context)


def send_welcome_email(user):
    """
    Send email to user account.
    Expects user account else returns false.
    """
    from django.utils.http import int_to_base36
    from django.contrib.auth.tokens import default_token_generator
    from tendenci.apps.site_settings.utils import get_setting

    token_generator = default_token_generator

    site_url = get_setting('site', 'global', 'siteurl')
    site_name = get_setting('site', 'global', 'sitedisplayname')

    # send new user account welcome email (notification)
    send_emails([user.email], 'user_welcome', {
        'site_url': site_url,
        'site_name': site_name,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'user': user,
        'username': user.username,
        'token': token_generator.make_token(user),
    })
