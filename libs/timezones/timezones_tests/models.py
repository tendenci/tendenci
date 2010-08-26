from django.db import models

from timezones.fields import TimeZoneField



class Profile(models.Model):
    name = models.CharField(max_length=100)
    timezone = TimeZoneField()
