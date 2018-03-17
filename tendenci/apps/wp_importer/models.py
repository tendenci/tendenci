from django.db import models
from django.contrib.auth.models import User
from tendenci.apps.files.models import File

class BlogImport(models.Model):
    # who made the import
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # when
    blog_import_date = models.DateTimeField(auto_now_add=True)
    # file
    blog = models.FileField(upload_to='blogimport')

class AssociatedFile(models.Model):
    post_id = models.IntegerField()
    file = models.ForeignKey(File, on_delete=models.CASCADE)
