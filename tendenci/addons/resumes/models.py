import uuid
import re

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from tendenci.core.base.fields import SlugField
from tendenci.addons.resumes.managers import ResumeManager
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.perms.models import TendenciBaseModel
from tinymce import models as tinymce_models
from tendenci.core.meta.models import Meta as MetaTags
from tendenci.addons.resumes.module_meta import ResumeMeta


def file_directory(instance, filename):
    filename = re.sub(r'[^a-zA-Z0-9._]+', '-', filename)
    return 'resumes/%d/%s' % (instance.id, filename)


class Resume(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    title = models.CharField(max_length=250)
    slug = SlugField(_('URL Path'), unique=True)
    description = tinymce_models.HTMLField()

    location = models.CharField(max_length=500, blank=True)  # cannot be foreign, needs to be open 'Texas' 'All 50 States' 'US and International'
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    awards = models.TextField(_('Awards and Certifications'), blank=True)
    education = models.TextField(blank=True)
    is_agency = models.BooleanField()  # defines if the resume posting is by a third party agency

    #TODO: do we need these fields?
    #desiredlocationstate = models.CharField(max_length=50)
    #desiredlocationcountry = models.CharField(max_length=50)
    #willingtorelocate = models.BooleanField()
    #workschedulepreferred = models.CharField(max_length=100)
    #compensationdesired = models.CharField(max_length=50)
    #licenses = models.CharField(max_length=100)
    #certifications = models.CharField(max_length=100)
    #expertise = models.CharField(max_length=800)
    #languages = models.CharField(max_length=120)

    # date related fields
    list_type = models.CharField(max_length=50, default='regular')  # premium or regular
    requested_duration = models.IntegerField(default=30)

    activation_dt = models.DateTimeField(null=True, blank=True)  # date resume listing was activated
    expiration_dt = models.DateTimeField(null=True, blank=True)  # date resume expires based on activation date and duration

    resume_url = models.CharField(max_length=300, blank=True)  # link to other (fuller) resume posting
    resume_file = models.FileField(_('Upload your resume here'), max_length=260,
                                    upload_to=file_directory, blank=True, default="")
    syndicate = models.BooleanField(_('Include in RSS feed'), blank=True)

    #TODO: foreign
    contact_name = models.CharField(max_length=150, blank=True)
    contact_address = models.CharField(max_length=50, blank=True)
    contact_address2 = models.CharField(max_length=50, blank=True)
    contact_city = models.CharField(max_length=50, blank=True)
    contact_state = models.CharField(max_length=50, blank=True)
    contact_zip_code = models.CharField(max_length=50, blank=True)
    contact_country = models.CharField(max_length=50, blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    contact_phone2 = models.CharField(max_length=50, blank=True)
    contact_fax = models.CharField(max_length=50, blank=True)
    contact_email = models.CharField(max_length=300, blank=True)
    contact_website = models.CharField(max_length=300, blank=True)

    # authority fields
    # allow_anonymous_view = models.BooleanField(_("Public can view"))
    # allow_user_view = models.BooleanField(_("Signed in user can view"))
    # allow_member_view = models.BooleanField()
    # allow_anonymous_edit = models.BooleanField()
    # allow_user_edit = models.BooleanField(_("Signed in user can change"))
    # allow_member_edit = models.BooleanField()

    # create_dt = models.DateTimeField(auto_now_add=True)
    # update_dt = models.DateTimeField(auto_now=True)
    # creator = models.ForeignKey(User, related_name="%(class)s_creator", editable=False, null=True, on_delete=models.SET_NULL)
    # creator_username = models.CharField(max_length=50, null=True)
    # owner = models.ForeignKey(User, related_name="%(class)s_owner", null=True, on_delete=models.SET_NULL)
    # owner_username = models.CharField(max_length=50, null=True)
    # status = models.BooleanField("Active", default=True)
    # status_detail = models.CharField(max_length=50, default='active')

    meta = models.OneToOneField(MetaTags, null=True)
    tags = TagField(blank=True)

    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = ResumeManager()

    class Meta:
        permissions = (("view_resume", _("Can view resume")),)

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return ResumeMeta().get_meta(self, name)

    @models.permalink
    def get_absolute_url(self):
        return ("resume", [self.slug])

    def save(self, *args, **kwargs):
        self.guid = self.guid or uuid.uuid1()
        super(Resume, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def is_pending(self):
        return self.status == 0 and self.status_detail == 'pending'
