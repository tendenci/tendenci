# django
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class ThemeFileVersion(models.Model):
    file_name  = models.CharField(max_length=200, blank=False)
    content = models.TextField(max_length=150000,blank=True)
    relative_file_path = models.CharField(max_length=500, blank=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    create_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = _('theme archive')
        verbose_name_plural = _('theme archives')
#         permissions = (("view_themefileversion",_("Can view theme version")),)
