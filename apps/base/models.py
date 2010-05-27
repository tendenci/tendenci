from django.db import models
from django.contrib.auth.models import User


# Abstract base class for authority fields
class AuditingBase(models.Model):
    STATUS_CHOICES = (('active','Active'),('inactive','Inactive'),)
    
    # authority fields
    allow_anonymous_view = models.BooleanField()
    allow_user_view = models.BooleanField()
    allow_member_view = models.BooleanField()
    allow_anonymous_edit = models.BooleanField()
    allow_user_edit = models.BooleanField()
    allow_member_edit = models.BooleanField()
    
    creator = models.ForeignKey(User, related_name="%(class)s_creator", editable=False)
    creator_username = models.CharField(max_length=50, editable=False)
    owner = models.ForeignKey(User, related_name="%(class)s_owner")    
    owner_username = models.CharField(max_length=50)
    status = models.BooleanField(default=True)
    status_detail = models.CharField(max_length=50, choices=STATUS_CHOICES,
                                     default='active')
    
    
    class Meta:
        abstract = True