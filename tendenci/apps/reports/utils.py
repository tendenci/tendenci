from django.contrib.contenttypes.models import ContentType


def get_ct_nice_name(ct_id):
    ct = ContentType.objects.get(pk=ct_id)
    if ct.model == "appentry":
        name = "Old Memberships"
    else:
        name = ct.app_label
    return name.replace('_', ' ').title()
