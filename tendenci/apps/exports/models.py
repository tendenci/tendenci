from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from picklefield.fields import PickledObjectField
from tendenci.apps.base.fields import SlugField
#from tendenci.apps.memberships.models import App

class Export(models.Model):
    STATUS_CHOICES = (
        ("completed", _(u"Completed")),
        ("pending", _(u"Pending")),
        ("failed", _(u"Failed")),
    )
    app_label = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    status = models.CharField(_(u"status"), max_length=50,
            default="pending", choices=STATUS_CHOICES)
    result = PickledObjectField(null=True, default=None)
    date_created = models.DateTimeField(auto_now_add=True)
    date_done = models.DateTimeField(auto_now=True)
    #memb_app = models.ForeignKey(App, blank=True, null=True)

    class Meta:
        app_label = 'exports'

    @models.permalink
    def get_absolute_url(self):
        return ("export.status", [self.app_label, self.model_name])

    def __unicode__(self):
        return "Export for %s %s" % (self.app_label, self.model_name)

