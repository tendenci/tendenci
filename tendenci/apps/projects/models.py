from builtins import str
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from tagging.fields import TagField
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.projects.managers import ProjectManager as NewProjectManager
from tendenci.apps.files.models import File
from tendenci.apps.files.managers import FileManager


class DocumentType(models.Model):
    type_name = models.CharField(_(u'type'), max_length=300)

    def __str__(self):
        return self.type_name

class ClientList(models.Model):
    name = models.CharField(_(u'name'), max_length=300)

    def __str__(self):
        return self.name


class CategoryPhoto(File):
    class Meta:
        app_label = 'projects'


class Category(models.Model):
    name = models.CharField(_(u'name'), max_length=300)
    image = models.ForeignKey(CategoryPhoto, help_text=_('Photo that represents this category.'), null=True, default=None, on_delete=models.CASCADE)
    position = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('position',)

    def save(self, *args, **kwargs):
        photo_upload = kwargs.pop('photo', None)
        super(Category, self).save(*args, **kwargs)

        if photo_upload and self.pk:
            image = CategoryPhoto(
                content_type=ContentType.objects.get_for_model(self.__class__),
                object_id=self.pk,
            )
            photo_upload.file.seek(0)
            image.file.save(photo_upload.name, photo_upload)  # save file row
            image.save()  # save image row

            if self.image:
                self.image.delete()  # delete image and file row
            self.image = image  # set image

            self.save()


class ProjectManager(models.Model):
    first_name = models.CharField(_(u'First Name'), max_length=200, blank=True)
    last_name = models.CharField(_(u'Last Name'), max_length=200, blank=True)

    def __str__(self):
        displayname = "%s %s" % (self.first_name, self.last_name)
        return displayname

class ProjectNumber(models.Model):
    number = models.CharField(_(u'number'), max_length=200, unique=True)

    def __str__(self):
        return self.number


class Project(TendenciBaseModel):

    STATUS_OPEN = 'open'
    STATUS_ASSIGNED = 'assigned'
    STATUS_IN_PROGRESS = 'in progress'
    STATUS_PENDING = 'pending'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = (
            (STATUS_OPEN, 'Open'),
            (STATUS_ASSIGNED, 'Assigned'),
            (STATUS_IN_PROGRESS, 'In Progress'),
            (STATUS_PENDING, 'Pending'),
            (STATUS_CLOSED, 'Closed')
        )

    tags = TagField(help_text='Tag 1, Tag 2, ...', blank=True)
    slug = models.SlugField(_(u'URL Path'), unique=True, max_length=200)
    project_name = models.CharField(
        _(u'Project Name'), max_length=300)
    project_manager = models.ForeignKey(ProjectManager, blank=True, null=True, on_delete=models.SET_NULL)
    project_number = models.OneToOneField(ProjectNumber, blank=True, null=True, on_delete=models.CASCADE)
    project_status = models.CharField(_(u'Project Status'),
        blank=True,
        max_length=50,
        choices=STATUS_CHOICES)

    cost = models.DecimalField(
        _(u'Project Cost'),
        max_digits = 10,
        decimal_places = 2,
        null = True,
        blank = True
        )
    client = models.ForeignKey(ClientList, blank=True, null=True, on_delete=models.SET_NULL)
    location = models.CharField(
        _(u'Location'), max_length=200, null = True, blank = True)
    city = models.CharField(
        _(u'City'), max_length=200, null = True, blank = True)
    state = models.CharField(_(u'State'), max_length=300, null = True,
        blank=True)
    start_dt = models.DateField(_(u'Project Start'), null=True, blank=True)
    end_dt = models.DateField(_(u'Project End'), null=True, blank=True)
    resolution = models.TextField(_(u'Resolution'), blank=True)
    project_description = models.TextField(_(u'Project Description'),
        blank=True)
    website_title = models.CharField(_(u'Project Website Title'),
        max_length=200, blank=True)
    website_url = models.URLField(_(u'Project Website URL'), max_length=200,
        blank=True)
    video_embed_code = models.TextField(_(u'Video Embed Code'),
        blank=True)
    video_title = models.CharField(_(u'Video Title'), max_length=200,
        blank=True)
    video_description = models.TextField(_(u'Video Description'),
        blank=True)
    category = models.ManyToManyField(Category, blank=True)
    perms = GenericRelation(ObjectPermission,
        object_id_field="object_id",
        content_type_field="content_type")

    objects = NewProjectManager()

    def __str__(self):
        return str(self.id)

#     class Meta:
#         permissions = (("view_project", "Can view project"),)

    def get_absolute_url(self):
        return reverse('projects.detail', args=[self.slug])

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self)


class Photo(File):
    project = models.ForeignKey(Project, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE)
    title = models.CharField(_(u'title'), max_length=200, blank=True)
    photo_description = models.TextField(_(u'Photo Description'), null=True, blank=True)

    objects = FileManager()

    def __str__(self):
        return self.title

class TeamMembers(File):
    project = models.ForeignKey(Project, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE)
    first_name = models.CharField(_(u'First Name'), max_length=200, blank=True)
    last_name = models.CharField(_(u'Last Name'), max_length=200, blank=True)
    title = models.CharField(_(u'Title'), max_length=200, blank=True)
    role = models.CharField(_(u'Role'), max_length=200, blank=True)
    team_description = models.TextField(_(u'Description'), null=True, blank=True)

    objects = FileManager()
    
    class Meta:
        verbose_name = _("Team Member")
        verbose_name_plural = _("Team Members")

    def __str__(self):
        return self.title

class Documents(File):
    project = models.ForeignKey(Project, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE)
    # renamed from type to doc_type because type clashes with the type in Files on upload
    doc_type = models.ForeignKey(DocumentType, blank=True, null=True, on_delete=models.CASCADE)
    other = models.CharField(_(u'other'), max_length=200, blank=True)
    document_dt = models.DateField(_(u'Document Date'), null=True, blank=True)

    objects = FileManager()

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
