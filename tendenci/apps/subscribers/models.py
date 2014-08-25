from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext, ugettext_lazy as _

from tendenci.apps.user_groups.models import Group
from tendenci.apps.forms_builder.forms.models import FormEntry, FieldEntry
from tendenci.apps.forms_builder.forms.settings import FIELD_MAX_LENGTH, LABEL_MAX_LENGTH

class GroupSubscription(models.Model):
    """
    This represents Group Subscriptions.
    It may or may not have a FormEntry for the subscriber's raw data.
    It will always have an associated SubscriberData.
    """
    group = models.ForeignKey(Group)
    subscriber = models.ForeignKey(FormEntry, related_name='subscriptions', null=True)
    create_dt = models.DateTimeField(auto_now_add=True, editable=False)
    update_dt = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('group', 'subscriber',)
        verbose_name = _("Group Subscription")
        verbose_name_plural = _("Group Subscriptions")

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.email)

    @property
    def name(self):
        if self.subscriber:
            return self.subscriber.get_name_email()[0]
        else:
            name_data = self.data.filter(field_label__icontains="name")
            if name_data:
                first_name = ""
                last_name = ""
                name = ""
                for obj in name_data:
                    field = obj.field_label
                    if 'full' in field.lower():
                        name = obj.value
                    if 'first' in field.lower():
                        first_name = obj.value
                    if 'last' in field.lower():
                        last_name = obj.value
                if not name:
                    if first_name or last_name:
                        name = '%s %s' % (first_name, last_name)
                if name:
                    return name
                else:
                    return name_data[0].value
        return None

    @property
    def email(self):
        if self.subscriber:
            return self.subscriber.get_name_email()[1]
        else:
            email_data = self.data.filter(field_label__in=["Email", "E-mail", "Email Address", "E-mail Address", "email address", "e-mail address", "e-mail", "email", "member_email", "Email (Required)"])
            if email_data:
                return email_data[0].value
        return None

class SubscriberData(models.Model):
    """
    Contains details for a subscriber.
    This is directly associated to a GroupSubscription.
    This may appear to be redundant data from the GroupSubscription's FormEntry field.
    But this is essentail for imported subscribers since the form is not imported with them.
    """
    subscription = models.ForeignKey(GroupSubscription, related_name="data")
    field_label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    value = models.CharField(_("Value"), max_length=FIELD_MAX_LENGTH)

    class Meta:
        unique_together = ('subscription', 'field_label')

    def __unicode__(self):
        return "%s(%s:%s)" % (self.subscription.pk, self.field_label, self.value)


def post_save_subscriber(sender, instance=None, created=False, **kwargs):
    if instance:
        from tendenci.apps.subscribers.utils import update_subscriber_data
        update_subscriber_data(instance.pk)

post_save.connect(post_save_subscriber, sender=GroupSubscription)
