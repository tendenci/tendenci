# -*- coding: utf-8 -*-


from django.db import migrations


def update_allow_anonymous_view(apps, schema_editor):
    """
    Set allow_anonymous_view to False for all profiles.
    """
    Profile = apps.get_model("profiles", "Profile")
    for p in Profile.objects.all():
        if p.allow_anonymous_view:
            Profile.objects.filter(id=p.id).update(allow_anonymous_view=False)


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_auto_20160330_1426'),
    ]

    operations = [
        # Commenting it out or maybe we should just delete this file.
        # It seems we don't need it - the allow_anonymous_view
        # does get updated when the hide_in_search field changes.
        #migrations.RunPython(update_allow_anonymous_view),
    ]
