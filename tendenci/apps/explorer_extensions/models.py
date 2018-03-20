from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse

from tendenci.apps.site_settings.utils import get_setting


class DatabaseDumpFile(models.Model):
    STATUS_CHOICES = (
        ("completed", _(u"Completed")),
        ("pending", _(u"Pending")),
        ("failed", _(u"Failed")),
        ("expired", _(u"Expired")),
    )
    FORMAT_CHOICES = (
        ("json", "json"),
        ("xml", "xml")
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    start_dt = models.DateTimeField(auto_now_add=True)
    end_dt = models.DateTimeField(null=True, blank=True)
    dbfile = models.FileField(upload_to='dbdump')
    status = models.CharField(max_length=50,
                default="pending", choices=STATUS_CHOICES)
    export_format = models.CharField(max_length=20,
                default="json", choices=FORMAT_CHOICES)

    @property
    def get_download_url(self):
        site_url = get_setting('site', 'global', 'siteurl')
        return "%s%s" % (site_url, reverse('explorer_extensions.download_dump', args=[self.pk]))


VALID_FORMAT_CHOICES = []
for choice in DatabaseDumpFile.FORMAT_CHOICES:
    VALID_FORMAT_CHOICES.append(choice[0])


@receiver(post_delete, sender=DatabaseDumpFile)
def dump_post_delete_handler(sender, **kwargs):
    inst = kwargs['instance']
    if inst.dbfile:
        inst.dbfile.delete(save=False)
