from django.db import models
from django.utils.translation import ugettext_lazy as _

from tendenci.addons.jobs.models import BaseJob
from tendenci.addons.locations.models import Location
from tendenci.addons.culintro.managers import CulintroJobManager

class CulintroJob(BaseJob):
    objects = CulintroJobManager()

    location_2 = models.ForeignKey(Location, blank=True, null=True)
    location_other = models.CharField(_('Location Other'), max_length=50, blank=True)
    open_call = models.BooleanField(_('Open call'), default=False)
    promote_posting = models.BooleanField(_('I want Culintro to promote my posting on other Job Board websites to increase viewership'), default=False)
    
    class Meta:
        permissions = (("view_culintro_job", "Can view culintro job"),)
        verbose_name = "Culintro Job"
        verbose_name_plural = "Culintro Jobs"
        
    @models.permalink
    def get_absolute_url(self):
        return ("culintro.detail", [self.slug])
