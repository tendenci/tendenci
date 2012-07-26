from django.db import models
from django.contrib.auth.models import User
from tendenci.core.files.models import File
from datetime import datetime

class BlogImport(models.Model):
    # who made the import
    author = models.ForeignKey(User)
    # when
    blog_import_date = models.DateTimeField(auto_now_add=True)
    # file
    blog = models.FileField(upload_to='blogimport')

class AssociatedFile(models.Model):
    post_id = models.IntegerField()
    file = models.ForeignKey(File)
