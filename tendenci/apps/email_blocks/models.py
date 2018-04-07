import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.models import TendenciBaseModel

class EmailBlock(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    email =models.EmailField()
    reason = models.CharField(max_length=500)
    email_domain = models.CharField(max_length=255)

    class Meta:
        app_label = 'email_blocks'
        permissions = (("view_email_block",_("Can view email block")),)

    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid4())
        self.email = self.email.lower()
        self.email_domain = self.email_domain.lower()

        super(EmailBlock, self).save(*args, **kwargs)
