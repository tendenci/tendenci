from django.db import models
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.redirects.managers import RedirectManager

HTTP_STATUS_CHOICES = (
    (301, _('301 - Permanent Redirect')),
    (302, _('302 - Temporary Redirect')),
)

STATUS_CHOICES = (
    (1,_('Active')),
    (0,_('Inactive')),
)

uses_regex_helptext = _("Check if the From URL uses a regular expression.")

class Redirect(models.Model):
    from_app = models.CharField(_('From App'), max_length=100, db_index=True, blank=True)
    from_url = models.CharField(_('From URL'), max_length=255, db_index=True, blank=True)
    to_url = models.CharField(_('To URL'), max_length=255, db_index=True,
        help_text=_("You may reference any named regex pattern in From URL with (name). e.g. (?P<slug>[\w\-\/]+) can be mapped to (slug)."))
    http_status = models.SmallIntegerField(_('HTTP Status'),choices=HTTP_STATUS_CHOICES, default=301)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    uses_regex = models.BooleanField(_('Uses Regular Expression'), default=False, help_text=uses_regex_helptext)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    objects = RedirectManager()

    class Meta:
        app_label = 'redirects'

    def __unicode__(self):
        if self.from_app:
            return "Redirect from App: %s" % self.from_app
        else:
            return "Redirect from URL: %s" % self.from_url
        
    def save(self, *args, **kwargs):
        if 'log' in kwargs:
            kwargs.pop('log')
        super(Redirect, self).save(*args, **kwargs)
