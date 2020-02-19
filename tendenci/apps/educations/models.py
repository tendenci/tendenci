from builtins import str

import uuid
import ast

from datetime import datetime

from django.db import models
#from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth.models import User

from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.educations.managers import EducationManager


class Education(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    school = models.CharField(_('School'), max_length=350)
    major = models.CharField(_('Major'), max_length=500)
    degree = models.CharField(_('Degree'), max_length=250)
    graduation_dt = models.DateTimeField(_('Graduation Date/Time'),
                                         null=True, blank=True)
    graduation_year = models.IntegerField(_('Graduation Year'), null=True, blank=True)
    user = models.ForeignKey(User, related_name="educations", on_delete=models.CASCADE)

    perms = GenericRelation(ObjectPermission,
                                  object_id_field="object_id",
                                  content_type_field="content_type")

    objects = EducationManager()

    def __init__(self, *args, **kwargs):
        super(Education, self).__init__(*args, **kwargs)
        # Handle the case that degree can be a a multi select field on membership forms
        # So make sure it shows as a string e.g. PHD, MS/MA rather than [u'PHD', u'MS/MA'],
        if self.degree:
            try:
                self.degree = ast.literal_eval(self.degree)
                if isinstance(self.degree, list):
                    self.degree = ', '.join(self.degree)
            except:
                pass

    class Meta:
#         permissions = (("view_education", _("Can view education")),)
        verbose_name = _("Education")
        verbose_name_plural = _("Educations")

    def __str__(self):
        return '%s - %s' %  (self.school, self.user)

#    def get_absolute_url(self):
#        return reverse('education', args=[self.pk])

    def save(self, *args, **kwargs):
        self.guid = self.guid or str(uuid.uuid4())
        if self.graduation_year and not self.graduation_dt:
            # placeholder to contain value for the datetime graduation field
            self.graduation_dt = datetime(year=self.graduation_year, month=1, day=1)

        super(Education, self).save(*args, **kwargs)
