from django.contrib.contenttypes.models import ContentType


def get_ct_nice_name(ct_id):
    if ct_id and ct_id != "None":
        ct = ContentType.objects.get(pk=ct_id)
        if ct.model == "appentry":
            name = "Old Memberships"
        elif ct.model == "membership":
            name = "T4 Memberships"
        elif ct.model == "event":
            name = "T4 Events"
        else:
            name = ct.app_label
    else:
        name = "Unspecified"
    return name.replace('_', ' ').title()
