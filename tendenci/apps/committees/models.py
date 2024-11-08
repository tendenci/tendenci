from datetime import date
from bs4 import BeautifulSoup

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.pages.models import BasePage
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.committees.managers import CommitteeManager
from tendenci.apps.committees.module_meta import CommitteeMeta
from tendenci.apps.user_groups.models import Group
from tendenci.apps.base.fields import SlugField
from tendenci.apps.files.models import File


class Committee(BasePage):
    """
    Committees Plugin. Similar to Pages with extra fields.
    """
    slug = SlugField(_('URL Path'), unique=True)
    mission = tinymce_models.HTMLField(null=True, blank=True)
    notes = tinymce_models.HTMLField(null=True, blank=True)
    sponsors =tinymce_models.HTMLField(blank=True, default='')
    featured_image = models.ForeignKey(File, null=True, default=None,
                              related_name='committees',
                              help_text=_('Only jpg, gif, or png images.'),
                              on_delete=models.SET_NULL)
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

    def save(self, *args, **kwargs):
        photo_upload = kwargs.pop('photo', None)

        super(Committee, self).save(*args, **kwargs)
        if photo_upload and self.pk:
            image = File(content_type=ContentType.objects.get_for_model(self.__class__),
                         object_id=self.pk,
                         creator=self.creator,
                         creator_username=self.creator_username,
                         owner=self.owner,
                         owner_username=self.owner_username)
            photo_upload.file.seek(0)
            image.file.save(photo_upload.name, photo_upload)
            image.save()

            self.featured_image = image
            self.save()

    def sponsor_image_urls(self):
        if self.sponsors:
            soup = BeautifulSoup(self.sponsors, 'html.parser')
            return [img['src'] for img in soup.find_all('img')]
        return None

    def update_group_perms(self, **kwargs):
        """
        Update the associated group perms for the officers of this chapter. 
        Grant officers the view and change permissions for their own group.
        """
        if not self.group:
            return
 
        ObjectPermission.objects.remove_all(self.group)
    
        perms = ['view', 'change']

        officer_users = [officer.user for officer in self.officers(
            ).filter(Q(expire_dt__isnull=True) | Q(expire_dt__gte=date.today()))]
        # include officers in chapters that are associated with this group
        for chapter in self.group.chapter_set.all():
            officer_users.extend([officer.user for officer in chapter.officers(
            ).filter(Q(expire_dt__isnull=True) | Q(expire_dt__gte=date.today()))])
        if officer_users:
            ObjectPermission.objects.assign(officer_users,
                                        self.group, perms=perms)
        

    def is_committee_leader(self, user):
        """
        Check if this user is one of the chapter leaders.
        """
        if not user.is_anonymous:
            return self.officers().filter(Q(expire_dt__isnull=True) | Q(
                expire_dt__gte=date.today())).filter(user=user).exists()

        return False


class Position(models.Model):
    title = models.CharField(_(u'title'), max_length=200)

    class Meta:
        app_label = 'committees'

    def __str__(self):
        return str(self.title)


class Officer(models.Model):
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE)
    user = models.ForeignKey(User,  related_name="committee_officers", on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=120, null=True, blank=True)
    expire_dt = models.DateField(_('Expire Date'), blank=True, null=True,
                                 help_text=_('Leave it blank if never expires.'))
                                 

    class Meta:
        app_label = 'committees'

    def __str__(self):
        return "%s" % self.pk
