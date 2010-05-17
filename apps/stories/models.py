from django.db import models

from base.models import AuditingBase

# Create your models here.
class Story(AuditingBase):
    guid = models.CharField(max_length=50, unique=False, blank=True)
    title = models.CharField(max_length=200, blank=True)
    content = models.CharField(max_length=1000, blank=True)
    syndicate = models.BooleanField()
    create_dt = models.DateTimeField(auto_now_add=True)
    fullstorylink = models.CharField(max_length=300, blank=True)
    start_dt = models.DateTimeField(null=True, blank=True)
    end_dt = models.DateTimeField(null=True, blank=True)
    ncsortorder = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return self.title