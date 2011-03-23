

def get_members_and_subscribers(group):
    members = group.groupmembership_set.all()
    subscribers = group.groupsubscriber_set.all()
    return {'members':members, 'subscribers':subscribers}
