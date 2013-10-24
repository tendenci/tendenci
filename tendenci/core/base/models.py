from django.db import models

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
