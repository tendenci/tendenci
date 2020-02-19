from builtins import str

from django.db import models
from django.urls import reverse
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
    sponsors =tinymce_models.HTMLField(blank=True, default='')
    contact_name = models.CharField(max_length=200, null=True, blank=True)
    contact_email = models.CharField(max_length=200, null=True, blank=True)
    join_link = models.CharField(max_length=200, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = CommitteeManager()

    def __str__(self):
        return str(self.title)

    class Meta:
#         permissions = (("view_committee", "Can view committee"),)
        app_label = 'committees'

    def get_absolute_url(self):
        return reverse('committees.detail', args=[self.slug])

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

    def __str__(self):
        return str(self.title)


class Officer(models.Model):
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE)
    user = models.ForeignKey(User,  related_name="%(app_label)s_%(class)s_user", on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        app_label = 'committees'

    def __str__(self):
        return "%s" % self.pk
