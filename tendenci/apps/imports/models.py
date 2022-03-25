import uuid
import re

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

def file_directory(instance, filename):
    filename = re.sub(r'[^a-zA-Z0-9._]+', '-', filename)
    uuid_hex = uuid.uuid4().hex[:8]
    #app_label = re.sub(r'[^a-zA-Z0-9._]+', '-', instance.app_label)
    return 'imports/%s/%s' % (uuid_hex, filename)


class Import(models.Model):
    STATUS_CHOICES = (
        ("pending", _(u"Pending")),
        ("processing", _(u"Processing")),
        ("completed", _(u"Completed")),
        ("failed", _(u"Failed")),
    )
    app_label = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    status = models.CharField(_(u"status"), max_length=50,
            default="pending", choices=STATUS_CHOICES)
    failure_reason = models.CharField(max_length=250, blank=True, default="")
    file = models.FileField("", max_length=260, upload_to=file_directory)
    total_created = models.IntegerField(default=0)
    total_updated = models.IntegerField(default=0)
    total_invalid = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_done = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('import.status', args=[self.app_label, self.model_name])

    def __str__(self):
        return "Import for %s %s" % (self.app_label, self.model_name)
