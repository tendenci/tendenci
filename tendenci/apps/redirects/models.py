from django.db import models
from django.utils.translation import ugettext_lazy as _

from redirects.managers import RedirectManager

HTTP_STATUS_CHOICES = (
    (301, '301 - Permanent Redirect'),
    (302, '302 - Temporary Redirect'),         
)

STATUS_CHOICES = (
    (1,'Active'),
    (0,'Inactive'),         
)

uses_regex_helptext = _("Check if the From URL uses a regular expression.")

class Redirect(models.Model):
    from_url = models.CharField(_('From URL'), max_length=255, unique=True, db_index=True)
    to_url = models.CharField(_('To URL'), max_length=255, db_index=True,
        help_text=_("You may reference any named regex pattern in From URL with (name). e.g. (?P<slug>[\w\-\/]+) can be mapped to (slug)."))
    http_status = models.SmallIntegerField(_('HTTP Status'),choices=HTTP_STATUS_CHOICES, default=301)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    uses_regex = models.BooleanField(_('Uses Regular Expression'), default=False, help_text=uses_regex_helptext)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
        
    objects = RedirectManager()
    
    def __unicode__(self):
        return "Redirect URL: %s" % self.from_url
