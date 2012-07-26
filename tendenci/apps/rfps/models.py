from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.apps.rfps.managers import RFPManager
from tendenci.core.files.models import file_directory, File

class Program(models.Model):
    title = models.CharField(_('title'), max_length=200, unique=True)
    
    def __unicode__(self):
        return self.title

class RFP(TendenciBaseModel):
    """
    RFPs plugin comments
    """
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    slug = models.SlugField(_(u'slug'), unique=True, blank=False, max_length=200, default=u'',)
    program = models.ForeignKey(Program, null=True, blank=True)
    name = models.CharField(_(u'name'), max_length=200,)
    rfp_status = models.CharField(_(u'status'), max_length=200, 
        choices=(('open','open'),('close','close'),))
    release_dt = models.DateTimeField(_(u'Release date'),)
    proposal_due_dt = models.DateTimeField(_(u'Proposal due date'),)
    expired_dt = models.DateTimeField(_(u'expired_dt'),)
    rfp_file = models.FileField(_(u'RFP file'), upload_to=file_directory)
    rfp_file_closed = models.FileField(_(u'RFP file closed'), upload_to=file_directory)
    questions_title = models.CharField(_(u'questions title'), max_length=200,)
    questions_expiration_dt = models.DateTimeField(_(u'questions expiration date'),)
    contract_doc = models.FileField(_(u'Standard Contract Document'), upload_to=file_directory)
    contract_doc_description = models.TextField(_(u'Standard Contract Document Description'),)
    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = RFPManager()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        permissions = (("view_rfp","Can view rfp"),)

    @models.permalink
    def get_absolute_url(self):
        return ("rfps.detail", [self.slug])
    
    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self)
