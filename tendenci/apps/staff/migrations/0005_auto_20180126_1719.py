# -*- coding: utf-8 -*-


from django.db import migrations


def make_slug_unique(apps, schema_editor):
    """
        The slug field should be unique
    """
    Staff = apps.get_model('staff', 'Staff')
    for staff in Staff.objects.all():
        if Staff.objects.filter(slug=staff.slug).exclude(id=staff.id).exists():
            staff.slug = '{0}-{1}'.format(staff.slug[:(75-len(str(staff.id))-1)], staff.id)
            staff.save()

class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0004_auto_20170309_1510'),
    ]

    operations = [
        migrations.RunPython(make_slug_unique),
    ]
