from django.db.models import Q
from tendenci.core.email_blocks.models import EmailBlock

# check if this email is listed in the email blocks
def listed_in_email_block(email_this):
    if email_this.find('@') <> -1:
        email_domain = email_this.split('@')[1]
        ebs = EmailBlock.objects.filter(Q(email=email_this) | Q(email_domain=email_domain))
        if ebs:
            return True
    return False