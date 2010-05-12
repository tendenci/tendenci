from django.db import models
from django.contrib.auth.models import User


# Abstract base class for authority fields
class AuthorityBase(models.Model):
    # authority fields
    creator = models.ForeignKey(User, related_name="%(class)s_creator")
    creator_username = models.CharField(max_length=50)
    owner = models.ForeignKey(User, related_name="%(class)s_owner")    
    owner_username = models.CharField(max_length=50)
    status = models.IntegerField()
    status_detail = models.CharField(max_length=50)
    
    
    class Meta:
        abstract = True