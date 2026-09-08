from django.db import models
from django.contrib.auth.models import User
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _


class Activity(models.Model):
    STATUS_CHOICES = (
                ('active', _('Active')),
                ('inactive', _('Inactive')),
                )
    user = models.ForeignKey(User, related_name="activities",
                             on_delete=models.CASCADE)
    activity_name = models.CharField(max_length=250)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    create_dt = models.DateTimeField(_("Created On"), auto_now_add=True)
    update_dt = models.DateTimeField(_("Last Updated"), auto_now=True)
    creator = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="activity_creator", editable=False)
    creator_username = models.CharField(max_length=150)
    owner = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="activity_owner")
    owner_username = models.CharField(max_length=150)
    status_detail = models.CharField(_("Status"),
                                     max_length=50,
                                     choices=STATUS_CHOICES,
                                     default='active')

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
        ordering = ('user__first_name', 'user__last_name', 'start_date',)

    def __str__(self):
        if self.start_date and self.end_date:
            return f'{self.user}: {self.activity_name} ({date_format(self.start_date, "SHORT_DATE_FORMAT")} - {date_format(self.end_date, "SHORT_DATE_FORMAT")})'
        elif self.start_date:
            return f'{self.user}: {self.activity_name} ({date_format(self.start_date, "SHORT_DATE_FORMAT")} - )'
        else:
            return f'{self.user}: {self.activity_name}'

