from django.db import models

from django.contrib.auth.models import User

class XMLExport (models.Model):
    # who made the import
    author = models.ForeignKey(User)
    # when
    xml_export_date = models.DateTimeField(auto_now_add=True)
    # file
    xml = models.FileField(upload_to='xmlexport')
