from django.db import models
from django.utils.translation import gettext_lazy as _

from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.libs.tinymce import models as tinymce_models

class SchoolCategory(models.Model):
    STATUS_CHOICES = (
                ('enabled', _('Enabled')),
                ('disabled', _('Disabled')),
                )
    name = models.CharField(_("Category Name"), max_length=150,
                             db_index=True, unique=True)
    status_detail = models.CharField(_('Status'),
                             max_length=10,
                             default='enabled',
                             choices=STATUS_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("School Category")
        verbose_name_plural = _("School Categories")
        app_label = 'trainings'


class Certification(models.Model):
    name = models.CharField(max_length=150, db_index=True, unique=True)
    period = models.PositiveSmallIntegerField()
    categories = models.ManyToManyField(SchoolCategory, through='CertCat')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Certification")
        verbose_name_plural = _("Certifications")
        app_label = 'trainings'


class CertCat(models.Model):
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE)
    category = models.ForeignKey(SchoolCategory, on_delete=models.CASCADE)
    required_credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.category.name} for {self.certification.name}'

    class Meta:
        unique_together = ('certification', 'category',)
        verbose_name = _("Certification Category")
        verbose_name_plural = _("Certification Categories")
        app_label = 'trainings'


class Course(TendenciBaseModel):
    LOCATION_TYPE_CHOICES = (
                ('online', _('Online')),
                ('onsite', _('Onsite')),
                )
    STATUS_CHOICES = (
                ('enabled', _('Enabled')),
                ('disabled', _('Disabled')),
                )
    name = models.CharField(_("Course Name"), max_length=150,
                            db_index=True, unique=True)
    location_type = models.CharField(_('Type'),
                             max_length=6,
                             default='online',
                             choices=LOCATION_TYPE_CHOICES)
    school_category = models.ForeignKey(SchoolCategory, null=True, on_delete=models.SET_NULL)
    course_code = models.CharField(max_length=50, blank=True, null=True)
    summary = models.TextField(blank=True, default='')
    description = tinymce_models.HTMLField(blank=True, default='')
    credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    min_score = models.DecimalField(max_digits=3, decimal_places=0, default=80)
    status_detail = models.CharField(_('Status'),
                             max_length=10,
                             default='enabled',
                             choices=STATUS_CHOICES)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        app_label = 'trainings'
    















