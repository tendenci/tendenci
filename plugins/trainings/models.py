from django.db import models
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField
from perms.models import TendenciBaseModel
from trainings.managers import TrainingManager, CompletionManager

TRAINING_TYPE_CHOICES = (
    ('Book', 'Book'),
    ('Conference', 'Conference'),
    ('Online Course', 'Online Course'),
    ('Internal Course', 'Internal Course'),
    ('External Course', 'External Course'),
)

class Training(TendenciBaseModel):
    """
    Trainings plugin for Schipul
    """
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    title = models.CharField(_(u'Title'), help_text=u'', blank=False, max_length=200, default=u'',)
    author_instructor = models.CharField(_(u'Author/Instructor'), help_text=u'Author, Instructor, or Training source. This can be a URL.', blank=True, max_length=200, default=u'',)
    description = models.TextField(_(u'Description'), help_text=u'', blank=True, default=u'',)
    training_type = models.CharField(_(u'Training Type'), help_text=u'', blank=False, max_length=50, choices=TRAINING_TYPE_CHOICES)
    points = models.DecimalField(_(u'Points'), max_digits=4, decimal_places=1, help_text=u'Try to round to the nearest .5', blank=False, default=1,)
    core_training = models.BooleanField(blank=True, default=0)
    source_id = models.CharField(_(u'Migration Id'), help_text=u'Migration ID used for migrating from other systems.', blank=True, null=True, max_length=200, default=u'',)
    objects = TrainingManager()
    
    def __unicode__(self):
        return unicode(self.title)
    
    class Meta:
        permissions = (("view_training","Can view training"),)
    
    @models.permalink
    def get_absolute_url(self):
        return ("trainings.detail", [self.pk])

class Completion(TendenciBaseModel):
    """
    Completions for trainings
    """
    feedback = models.TextField(_(u'Feedback'), help_text=u'Comments about the training.', blank=True, default=u'',)
    finish_dt = models.DateTimeField(_('Completion Date'), null=True, blank=False)
    training = models.ForeignKey('Training', blank=False)
    objects = CompletionManager()
    
    def __unicode__(self):
        return unicode(self.id)
    
    class Meta:
        permissions = (("view_completion","Can view completion"),)
    
    @models.permalink
    def get_absolute_url(self):
        return ("completion.detail", [self.pk])

