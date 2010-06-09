from django.db import models

STATUS_CHOICES = (('active','Active'),('inactive','Inactive'),)

class Robot(models.Model):
    name = models.CharField(max_length=150)
    url = models.URLField()
    version = models.CharField(max_length=50)
    status = models.BooleanField(default=True)
    status_detail = models.CharField(max_length=50, choices=STATUS_CHOICES,default='active')