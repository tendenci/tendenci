from django.db import models

class Report404(models.Model):
    url = models.CharField(max_length=200)
    count = models.IntegerField(default=1)
