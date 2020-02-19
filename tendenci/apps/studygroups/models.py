from builtins import str

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.pages.models import BasePage
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.studygroups.managers import StudyGroupManager
from tendenci.apps.studygroups.module_meta import StudyGroupMeta
from tendenci.apps.user_groups.models import Group, GroupMembership


class StudyGroup(BasePage):
    """
    StudyGroups Plugin. Similar to Pages with extra fields.
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

    objects = StudyGroupManager()

    def __str__(self):
        return str(self.title)

    class Meta:
#         permissions = (("view_studygroup", "Can view studygroup"),)
        app_label = 'studygroups'

    def get_absolute_url(self):
        return reverse('studygroups.detail', args=[self.slug])

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return StudyGroupMeta().get_meta(self, name)

    def officers(self):
        return Officer.objects.filter(study_group=self).order_by('pk')


class Position(models.Model):
    title = models.CharField(_(u'title'), max_length=200)
    group = models.ForeignKey(Group, help_text='Group with associated permissions for this officer position.', null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'studygroups'

    def __str__(self):
        return str(self.title)


class Officer(models.Model):
    study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        app_label = 'studygroups'

    def __str__(self):
        return "%s" % self.pk

    def save(self, *args, **kwargs):
        if self.pk:
            old_officer = Officer.objects.get(pk=self.pk)
            if old_officer.position and old_officer.position.group and old_officer.user:
                gm = GroupMembership.objects.filter(member=old_officer.user, group=old_officer.position.group)[:1]
                if gm:
                    gm[0].delete()

        super(Officer, self).save(*args, **kwargs)
        officer = self

        if officer.position:
            if officer.position.group and officer.user:
                try:
                    GroupMembership.objects.get(member=officer.user, group=officer.position.group)
                except:
                    GroupMembership.add_to_group(member=officer.user, group=officer.position.group)

        return officer
