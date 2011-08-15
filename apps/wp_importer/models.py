from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class BlogImport(models.Model):
    # who made the import
    author = models.ForeignKey(User)
    # when
    blog_import_date = models.DateTimeField(auto_now_add=True)
    # file
    blog = models.FileField(upload_to='blogimport')
