from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from picklefield.fields import PickledObjectField

class ICS(models.Model):
    class Meta:
        verbose_name_plural = 'ics'

    STATUS_CHOICES = (
        ("completed", _(u"Completed")),
        ("pending", _(u"Pending")),
        ("failed", _(u"Failed")),
    )
    app_label = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(_(u"status"), max_length=50,
            default="pending", choices=STATUS_CHOICES)
    result = PickledObjectField(null=True, default=None)
    date_created = models.DateTimeField(auto_now_add=True)
    date_done = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('ics.status', args=[self.app_label, self.model_name])

    def __str__(self):
        return "ICS for %s %s - %s" % (self.app_label, self.model_name, self.user)
