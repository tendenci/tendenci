from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

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
    enable_diamond = models.BooleanField(default=False,
                                help_text=_("Enable diamond to be added"))
    diamond_name = models.CharField(max_length=50, blank=True, default='Diamond')
    diamond_required_credits = models.DecimalField(_("Required Credits"),
                                                   blank=True,
                                    max_digits=5, decimal_places=2, default=0)
    diamond_required_online_credits = models.DecimalField(_("Required Online Credits"),
                                                          blank=True, 
                                    max_digits=5, decimal_places=2, default=0)
    diamond_period = models.PositiveSmallIntegerField(_("Period"), blank=True, default=12)
    diamond_required_activity = models.PositiveSmallIntegerField(_("Required Teaching Activity"),
                                                                blank=True, default=1)

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
    min_score = models.PositiveSmallIntegerField(default=80)
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
    

class Exam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # instead of course, maybe need to tie to exam (when available)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.PositiveSmallIntegerField(default=0)
    create_dt = models.DateTimeField(_("Created On"), auto_now_add=True)
    update_dt = models.DateTimeField(_("Date"), auto_now=True)
    creator = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="trainings_exams_created", editable=False)
    owner = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="trainings_exams_updated")
    
    def __str__(self):
        return f'Exam for {self.user} on {self.course}'

    class Meta:
        verbose_name = _("Exam")
        verbose_name_plural = _("Exams")
        app_label = 'trainings'


class Transcript(models.Model):
    LOCATION_TYPE_CHOICES = (
                ('online', _('Online')),
                ('outside', _('Outside')),
                ('onsite', _('Onsite')),
                )
    # APPLIED_CHOICES = (
    #             ('D', _('Designated')),
    #             ('C', _('Cancelled')),
    #             )
    STATUS_CHOICES = (
                ('pending', _('Pending')),
                ('approved', _('Approved')),
                ('cancelled', _('Cancelled')),
                )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    school_category = models.ForeignKey(SchoolCategory,
                                        null=True, on_delete=models.SET_NULL)
    location_type = models.CharField(_('Type'),
                             max_length=10,
                             default='online',
                             choices=LOCATION_TYPE_CHOICES)
    credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # applied = models.CharField(max_length=1, default='D',
    #                          choices=APPLIED_CHOICES)
    status = models.CharField(max_length=10, default='pending',
                             choices=STATUS_CHOICES)
    certification_track = models.ForeignKey(Certification,
                                   null=True, on_delete=models.SET_NULL)
    registrant_id = models.IntegerField(blank=True, default=0)
    external_id = models.CharField(max_length=50, default='')
    create_dt = models.DateTimeField(_("Created On"), auto_now_add=True)
    update_dt = models.DateTimeField(_("Last Updated"), auto_now=True)
    creator = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="trainings_transcripts_created", editable=False)
    owner = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="trainings_transcripts_updated")
    
    def __str__(self):
        return f'transcript for {self.user}'

    class Meta:
        verbose_name = _("Transcript")
        verbose_name_plural = _("Transcripts")
        app_label = 'trainings'
    














