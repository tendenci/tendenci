from django.contrib.contenttypes.models import ContentType


def get_ct_nice_name(ct_id):
    if ct_id and ct_id != "None":
        ct = ContentType.objects.get(pk=ct_id)
        if ct.model == "appentry":
            name = "Memberships - Old"
        elif ct.model == "membership":
            name = "Memberships - T4"
        elif ct.model == "membershipdefault":
            name = "Memberships - Ind"
        elif ct.model == "corporatemembership":
            name = "Corp Memberships - Old"
        elif ct.model == "corpmembrenewentry":
            name = "Corp Memberships - Old Renew"
        elif ct.model == "event":
            name = "Events - T4"
        else:
            name = ct.app_label
    else:
        name = "Unspecified"
    return name.replace('_', ' ').title()
