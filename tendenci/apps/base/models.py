from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from tendenci.libs.abstracts.models import OrderingBaseModel
from tendenci.core.base.fields import DictField


class UpdateTracker(models.Model):
    is_updating = models.BooleanField(default=False)

    @classmethod
    def get_or_create_instance(cls):
        try:
            instance = UpdateTracker.objects.get()
        except UpdateTracker.DoesNotExist:
            instance = UpdateTracker(is_updating=False)
            instance.save()
        return instance

    @classmethod
    def start(cls):
        tracker = UpdateTracker.get_or_create_instance()
        tracker.is_updating = True
        tracker.save()

    @classmethod
    def end(cls):
        tracker = UpdateTracker.get_or_create_instance()
        tracker.is_updating = False
        tracker.save()

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(UpdateTracker, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s: status = %s" % (self.id, self.is_updating)


class ChecklistItem(OrderingBaseModel):
    key = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=200)
    done = models.BooleanField(default=False)

    def __unicode__(self):
        return self.label


class BaseImport(models.Model):
    OVERRIDE_CHOICES = (
        (0, _('Blank Fields')),
        (1, _('All Fields (override)')),
    )

    STATUS_CHOICES = (
        ('not_started', _('Not Started')),
        ('preprocessing', _('Pre_processing')),
        ('preprocess_done', _('Pre_process Done')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
    )

    # store the header line to assist in generating recap
    header_line = models.CharField(_('Header Line'), max_length=3000, default='')

    # overwrite already existing fields if match
    override = models.IntegerField(choices=OVERRIDE_CHOICES, default=0)
    # uniqueness key
    key = models.CharField(_('Key'), max_length=50)

    total_rows = models.IntegerField(default=0)
    num_processed = models.IntegerField(default=0)
    summary = models.CharField(_('Summary'), max_length=500,
                           null=True, default='')
    status = models.CharField(choices=STATUS_CHOICES,
                              max_length=50,
                              default='not_started')
    complete_dt = models.DateTimeField(null=True)

    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    create_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def get_file(self):
        return self.upload_file

    def __unicode__(self):
        return self.get_file().file.name


class BaseImportData(models.Model):
    # dictionary object representing a row in csv
    row_data = DictField(_('Row Data'))
    # the original row number in the uploaded csv file
    row_num = models.IntegerField(_('Row #'))
    # action_taken can be 'insert', 'update' or 'mixed'
    action_taken = models.CharField(_('Action Taken'), max_length=20, null=True)
    error = models.CharField(_('Error'), max_length=500, default='')

    class Meta:
        abstract = True
