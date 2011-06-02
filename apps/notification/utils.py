from perms.utils import get_notice_recipients
from notification.models import send_emails

def send_notifications(scope, scope_category, name, label, extra_context=None):
    """
        a small wrapper for sending notification emails to 
        recipients specified in site_settings.
    """
    recipients = get_notice_recipients(scope, scope_category, name)
    if recipients:
        send_emails(recipients, label, extra_context)
