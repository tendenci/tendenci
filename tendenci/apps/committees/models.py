from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.pages.models import BasePage
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.committees.managers import CommitteeManager
from tendenci.apps.committees.module_meta import CommitteeMeta
from tendenci.apps.user_groups.models import Group


class Committee(BasePage):
    """
    Committees Plugin. Similar to Pages with extra fields.
    """

    mission = tinymce_models.HTMLField(null=True, blank=True)
    notes = tinymce_models.HTMLField(null=True, blank=True)
    contact_name = models.CharField(max_length=200, null=True, blank=True)
    contact_email = models.CharField(max_length=200, null=True, blank=True)
    join_link = models.CharField(max_length=200, null=True, blank=True)
    group = models.ForeignKey(Group)

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = CommitteeManager()

    def __unicode__(self):
        return unicode(self.title)

    class Meta:
        permissions = (("view_committee", "Can view committee"),)
        app_label = 'committees'

    @models.permalink
    def get_absolute_url(self):
        return ("committees.detail", [self.slug])

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return CommitteeMeta().get_meta(self, name)

    def officers(self):
        return Officer.objects.filter(committee=self).order_by('pk')


class Position(models.Model):
    title = models.CharField(_(u'title'), max_length=200)

    class Meta:
        app_label = 'committees'

    def __unicode__(self):
        return unicode(self.title)


class Officer(models.Model):
    committee = models.ForeignKey(Committee)
    user = models.ForeignKey(User,  related_name="%(app_label)s_%(class)s_user")
    position = models.ForeignKey(Position)
    phone = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        app_label = 'committees'

    def __unicode__(self):
        return "%s" % self.pk
