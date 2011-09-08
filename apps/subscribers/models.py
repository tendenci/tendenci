from django.db import models
from forms_builder.forms.models import FormEntry, FieldEntry
from user_groups.models import Group

class GroupSubscription(models.Model):
    group = models.ForeignKey(Group)
    subscriber = models.ForeignKey(FormEntry, related_name='subscriptions')
    
    create_dt = models.DateTimeField(auto_now_add=True, editable=False)
    update_dt = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return "%s - %s" % (self.subscriber.pk , self.group.name)
        
    @property
    def name(self):
        return self.subscriber.get_name_email()[0]
        
    @property
    def email(self):
        return self.subscriber.get_name_email()[1]
    
    class Meta:
        unique_together = ('group', 'subscriber',)
        verbose_name = "Group Subscription"
        verbose_name_plural = "Group Subscriptions"
