from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType

from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.files.models import File
from tagging.fields import TagField
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.testimonials.managers import TestimonialManager
from tendenci.libs.abstracts.models import OrderingBaseModel


class TestimonialPhoto(File):
    class Meta:
        app_label = 'testimonials'
        manager_inheritance_from_future = True


class Testimonial(OrderingBaseModel, TendenciBaseModel):
    first_name = models.CharField(max_length=50, blank=True, default="")
    last_name = models.CharField(max_length=50, blank=True, default="")
    city = models.CharField(max_length=50, blank=True, default="")
    state = models.CharField(max_length=25, blank=True, default="")
    country = models.CharField(max_length=50, blank=True, default="")
    email = models.EmailField(max_length=75, blank=True, default="")
    company = models.CharField(max_length=75, blank=True, default="")
    title = models.CharField(max_length=50, blank=True, default="")
    website = models.URLField(max_length=255, blank=True, null=True)
    testimonial = models.TextField(help_text=_('Supports &lt;strong&gt;, &lt;em&gt;, and &lt;a&gt; HTML tags.'))
    image = models.ForeignKey(TestimonialPhoto,
        on_delete=models.SET_NULL,
        help_text=_('Photo for this testimonial.'), null=True, default=None)
    tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = TestimonialManager()

    class Meta:
#         permissions = (("view_testimonial","Can view testimonial"),)
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['position']
        app_label = 'testimonials'

    def __str__(self):
        return '%s %s %s' % (self.first_name, self.last_name, self._meta.verbose_name)

    def get_absolute_url(self):
        return reverse('testimonial.view', args=[self.pk])

    def first_last_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def photo(self):
        if self.image and self.image.file:
            return self.image.file

        return None

    def save(self, *args, **kwargs):
        photo_upload = kwargs.pop('photo', None)

        if self.pk is None:
            # Append to top of the list on add
            try:
                last = Testimonial.objects.all().order_by('-position')[0]
                if last.position:
                    self.position = int(last.position) + 1
                else:
                    self.position = 1
            except IndexError:
                # First row
                self.position = 1

        super(Testimonial, self).save(*args, **kwargs)

        if photo_upload and self.pk:
            image = TestimonialPhoto(
                content_type=ContentType.objects.get_for_model(self.__class__),
                object_id=self.pk,
                creator=self.creator,
                creator_username=self.creator_username,
                owner=self.owner,
                owner_username=self.owner_username
                    )
            photo_upload.file.seek(0)
            image.file.save(photo_upload.name, photo_upload)  # save file row
            image.save()  # save image row

            if self.image:
                self.image.delete()  # delete image and file row
            self.image = image  # set image

            self.save()
