from subscribers.models import SubscriberData, GroupSubscription

def get_members_and_subscribers(group):
    members = group.groupmembership_set.all()
    subscribers = group.groupsubscriber_set.all()
    return {'members':members, 'subscribers':subscribers}

def update_subscriber_data(sub_pk):
    """
    Given a GroupSubscription pk, create all the SubscriberData for it.
    """
    sub = GroupSubscription.objects.get(pk=sub_pk)
    if sub.subscriber: # imported subscribers do not have this
        for field in sub.subscriber.fields.all():
            try:
                data = SubscriberData.objects.get(subscription=sub, field_label=field.field.label)
            except SubscriberData.DoesNotExist:
                data = SubscriberData(subscription = sub, field_label=field.field.label)
            data.value = field.value
            data.save()
