from tendenci.core.perms.utils import get_notice_recipients
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
    from tendenci.core.site_settings.utils import get_setting

    token_generator = default_token_generator

    site_url = get_setting('site', 'global', 'siteurl')
    site_name = get_setting('site', 'global', 'sitedisplayname')

    # send new user account welcome email (notification)
    send_emails([user.email], 'user_welcome', {
        'site_url': site_url,
        'site_name': site_name,
        'uid': int_to_base36(user.id),
        'user': user,
        'username': user.username,
        'token': token_generator.make_token(user),
    })
