from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

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
    author = models.ForeignKey(User)
    start_dt = models.DateTimeField(auto_now_add=True)
    end_dt = models.DateTimeField(null=True, blank=True)
    dbfile = models.FileField(upload_to='dbdump')
    status = models.CharField(max_length=50,
                default="pending", choices=STATUS_CHOICES)
    export_format = models.CharField(max_length=20,
                default="json", choices=FORMAT_CHOICES)

VALID_FORMAT_CHOICES = []
for choice in DatabaseDumpFile.FORMAT_CHOICES:
    VALID_FORMAT_CHOICES.append(choice[0])
