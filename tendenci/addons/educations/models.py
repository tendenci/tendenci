import uuid

from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.addons.educations.managers import EducationManager


class Education(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    school = models.CharField(_('School'), max_length=350)
    major = models.CharField(_('Major'), max_length=500)
    degree = models.CharField(_('Degree'), max_length=250)
    graduation_dt = models.DateTimeField(_('Graduation Date/Time'),
                                         null=True, blank=True)
    graduation_year = models.IntegerField(_('Graduation Year'), null=True, blank=True)
    user = models.ForeignKey(User, related_name="educations")

    perms = generic.GenericRelation(ObjectPermission,
                                  object_id_field="object_id",
                                  content_type_field="content_type")

    objects = EducationManager()

    class Meta:
        permissions = (("view_education", _("Can view education")),)
        verbose_name = _("Education")
        verbose_name_plural = _("Educations")

    def __unicode__(self):
        return '%s - %s' %  (self.school, self.user)

#    @models.permalink
#    def get_absolute_url(self):
#        return ("education", [self.pk])

    def save(self, *args, **kwargs):
        self.guid = self.guid or unicode(uuid.uuid1())
        if self.graduation_year and not self.graduation_dt:
            # placeholder to contain value for the datetime graduation field
            self.graduation_dt = datetime(year=self.graduation_year, month=1, day=1)

        super(Education, self).save(*args, **kwargs)
