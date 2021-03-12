from builtins import str

from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.pages.models import BasePage
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.chapters.managers import ChapterManager
from tendenci.apps.chapters.module_meta import ChapterMeta
from tendenci.apps.user_groups.models import Group
from tendenci.apps.entities.models import Entity
from tendenci.apps.files.models import File


class Chapter(BasePage):
    """
    Chapters module. Similar to Pages with extra fields.
    """
    entity = models.OneToOneField(Entity, null=True,
                                  on_delete=models.SET_NULL,)
    mission = tinymce_models.HTMLField(null=True, blank=True)
    notes = tinymce_models.HTMLField(null=True, blank=True)
    sponsors =tinymce_models.HTMLField(blank=True, default='')
    featured_image = models.ForeignKey(File, null=True, default=None,
                              related_name='chapters',
                              help_text=_('Only jpg, gif, or png images.'),
                              on_delete=models.SET_NULL)
    contact_name = models.CharField(max_length=200, null=True, blank=True)
    contact_email = models.CharField(max_length=200, null=True, blank=True)
    join_link = models.CharField(max_length=200, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = ChapterManager()

    def __str__(self):
        return str(self.title)

    class Meta:
        app_label = 'chapters'

    def get_absolute_url(self):
        return reverse('chapters.detail', args=[self.slug])

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return ChapterMeta().get_meta(self, name)

    def officers(self):
        return Officer.objects.filter(chapter=self).order_by('pk')
    
    def save(self, *args, **kwargs):
        photo_upload = kwargs.pop('photo', None)

        super(Chapter, self).save(*args, **kwargs)
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


class Position(models.Model):
    title = models.CharField(_(u'title'), max_length=200)

    class Meta:
        app_label = 'chapters'

    def __str__(self):
        return str(self.title)


class Officer(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    user = models.ForeignKey(User,  related_name="%(app_label)s_%(class)s_user", on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        app_label = 'chapters'

    def __str__(self):
        return "%s" % self.pk
