from django.db import models
from django.utils.translation import gettext_lazy as _

from tendenci.apps.robots.managers import RobotManager


STATUS_CHOICES = (('active',_('Active')),('inactive',_('Inactive')),)

class Robot(models.Model):
    name = models.CharField(max_length=150)
    url = models.URLField()
    version = models.CharField(max_length=50)
    status = models.BooleanField(default=True)
    status_detail = models.CharField(max_length=50, choices=STATUS_CHOICES,default='active')

    objects = RobotManager()

    class Meta:
        app_label = 'robots'

    def __str__(self):
        return self.name
