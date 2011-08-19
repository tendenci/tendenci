from django.db import models
from django.utils.translation import ugettext_lazy as _


class Metric(models.Model):
    """
    Metrics for the sites usage
    """
    users = models.IntegerField(_('users'))
    members = models.IntegerField(_('members'))
    visits = models.IntegerField(_('visits'))
    disk_usage = models.BigIntegerField(_('disk usage'))
    create_dt = models.DateTimeField(_('create date/time'), auto_now_add=True)

    def __unicode__(self):
        return 'Metrics: %d' % self.pk
