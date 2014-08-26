import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tendenci.core.perms.models import TendenciBaseModel

class EmailBlock(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    email =models.CharField(max_length=255)
    reason = models.CharField(max_length=500)
    email_domain = models.CharField(max_length=255)

    class Meta:
        permissions = (("view_email_block",_("Can view email block")),)

    @models.permalink
    def get_absolute_url(self):
        return ("email_block.view", [self.pk])

    def save(self, user=None):
        if not self.id:
            self.guid = str(uuid.uuid1())
            if user and user.id:
                self.creator=user
                self.creator_username=user.username
        if user and user.id:
            self.owner=user
            self.owner_username=user.username

        super(EmailBlock, self).save()

    # if this email allows view by user2_compare
    def allow_view_by(self, user2_compare):
        boo = False

        if user2_compare.profile.is_superuser:
            boo = True
        else:
            if user2_compare == self.creator or user2_compare == self.owner:
                if self.status:
                    boo = True
            else:
                if user2_compare.has_perm('email_blocks.view_email_block', self):
                    if self.status == 1 and self.status_detail=='active':
                        boo = True
        return boo

    # if this email allows edit by user2_compare
    def allow_edit_by(self, user2_compare):
        boo = False
        if user2_compare.profile.is_superuser:
            boo = True
        else:
            if user2_compare == self.user:
                boo = True
            else:
                if user2_compare == self.creator or user2_compare == self.owner:
                    if self.status:
                        boo = True
                else:
                    if user2_compare.has_perm('email_blocks.edit_email_block', self):
                        if self.status:
                            boo = True
        return boo
