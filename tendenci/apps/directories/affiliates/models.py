from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
 
from tendenci.apps.directories.models import Directory
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.corporate_memberships.models import CorporateMembershipType
from tendenci.apps.memberships.models import MembershipType

 
class AffiliateRequest(models.Model):
    to_directory = models.ForeignKey(Directory, related_name='to_directory',
                                       on_delete=models.CASCADE)
    from_directory = models.ForeignKey(Directory, related_name='from_directory',
                                            on_delete=models.CASCADE)
    create_dt = models.DateTimeField(_("Created On"), auto_now_add=True)
    creator = models.ForeignKey(User, null=True, default=None,
                                on_delete=models.SET_NULL,
                                editable=False)
 
    class Meta:
        app_label = 'directories'
 
 
class RequestEmail(models.Model):
    """
    The emails for request to associate.
    """
    affiliate_request = models.ForeignKey(AffiliateRequest, null=True, on_delete=models.SET_NULL)
    sender = models.ForeignKey(User,
        null=True, on_delete=models.SET_NULL)
    recipients = models.CharField(max_length=255, blank=True, default='')
    message = models.TextField(blank=False)
    create_dt = models.DateTimeField(_("Created On"), auto_now_add=True)
    creator = models.ForeignKey(User, related_name="affiliate_requestemail_creator",
                                null=True, default=None,
                                on_delete=models.SET_NULL,
                                editable=False)

    class Meta:
        app_label = 'directories'

    def __str__(self):
        return 'Submission for %s' % self.affiliate_request


class AllowedConnection(models.Model):
    """
    This model stores the allowed connection for marketplace listings (directories).
    
    Each corp type can allow multiple member types.
    """
    corp_type = models.OneToOneField(CorporateMembershipType, on_delete=models.CASCADE)
    member_types = models.ManyToManyField(MembershipType)
    
    class Meta:
        ordering = ("corp_type",)
        app_label = 'directories'
