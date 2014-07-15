from django.db import models
from django.contrib.auth.models import User

class APIAccessKey(models.Model):
    access_id = models.CharField(max_length=50, unique=True)
    secret_key = models.CharField(max_length=50)
    client_name = models.CharField(max_length=200, default='')
    client_url = models.CharField(max_length=200, default='')

    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, related_name="apiaccesskey_creator",  null=True)
    update_dt = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)