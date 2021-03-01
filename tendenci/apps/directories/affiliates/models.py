from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
 
from tendenci.apps.directories.models import Directory, Category

 
class AffiliateRequest(models.Model):
    to_directory = models.ForeignKey(Directory, related_name='to_directory',
                                       on_delete=models.CASCADE)
    from_directory = models.ForeignKey(Directory, related_name='from_directory',
                                            on_delete=models.CASCADE)
    request_as = models.ForeignKey(Category, related_name='affiliate_requests',
                                 null=True, on_delete=models.CASCADE)
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
    affiliate_request = models.ForeignKey(AffiliateRequest, null=True,
                                          related_name='request_emails',
                                           on_delete=models.CASCADE)
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


class Connection(models.Model):
    """
    This model defines the connections for marketplace listings (directories).
    
    Each category can have multiple categories to be associated with.
    """
    cat = models.OneToOneField(Category, verbose_name=_("Category"), related_name='connections', on_delete=models.CASCADE)
    affliated_cats = models.ManyToManyField(Category, verbose_name=_("Affliated Categories"), related_name='allowed_connections')
    
    class Meta:
        verbose_name = _("Allowed Connection")
        verbose_name_plural = _("Allowed Connections")
        ordering = ("cat",)
        app_label = 'directories'
