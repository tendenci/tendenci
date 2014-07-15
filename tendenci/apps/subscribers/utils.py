from tendenci.apps.subscribers.models import SubscriberData, GroupSubscription

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

def get_subscriber_name_email(field_list):
    """Try to figure out the name and email from a subscriber
        that doesn't have a form entry
    """
    first_name = ""
    last_name = ""
    name = ""
    email = ""
    for obj in field_list:
        field = obj.field_label
        if 'email' in field.lower():
            email = obj.value
        if 'full' in field.lower():
            name = obj.value
        if 'first' in field.lower():
            first_name = obj.value
        if 'last' in field.lower():
            last_name = obj.value
    if not name:
        if first_name or last_name:
            name = '%s %s' % (first_name, last_name)
    if not name:
        # pick the name from email
        if email:
            if  '@' in email:
                name, domain = email.split('@')
            else:
                name = email

    return (name, email)
