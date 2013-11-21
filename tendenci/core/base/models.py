from django.db import models

from tendenci.libs.abstracts.models import OrderingBaseModel


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
