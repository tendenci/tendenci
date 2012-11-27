from django.contrib.auth.models import User
from tendenci.apps.user_groups.models import Group

def member_choices(group, member_label):
    """
    Creates a list of 2 tuples of a user's pk and the selected
    member label. This is used for generating choices for a form.
    choices for member label are: email, full name and username.
    """
    members = User.objects.filter(is_active=1)
    if member_label == 'email':
        label = lambda x: x.email
    elif member_label == 'full_name':
        label = lambda x: x.get_full_name()
    else:
        label = lambda x: x.username
    choices = []
    for member in members:
        choices.append((member.pk, label(member)))
    return choices


def get_default_group():
    """
    get lowest id group to use as default in other apps that FK to Group
    """
    return (Group.objects.filter(
        status=True, status_detail="active").order_by('id')[:1] or [None])[0]
