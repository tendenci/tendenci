from django.db import models
from forms_builder.forms.models import FormEntry
from user_groups.models import Group

# Create your models here.
class GroupSubscription(models.Model):
    group = models.ForeignKey(Group)
    subscriber = models.ForeignKey(FormEntry, related_name='group_subscriber')
    
    create_dt = models.DateTimeField(auto_now_add=True, editable=False)
    update_dt = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return "%s - %s" % (self.subscriber.pk , self.group.name)
    
    class Meta:
        unique_together = ('group', 'subscriber',)
        verbose_name = "Group Subscription"
        verbose_name_plural = "Group Subscriptions"
