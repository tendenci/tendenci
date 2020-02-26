# -*- coding: utf-8 -*-


from django.db import migrations
from django.template.defaultfilters import slugify

def assign_slug(apps, schema_editor):
    """
        Assign value to the slug field for existing department rows
    """
    Department = apps.get_model('staff', 'Department')
    for department in Department.objects.all():
        if not department.slug:
            slug = slugify(department.name)
            if Department.objects.filter(slug=slug).exists():
                slug = '%s%s' % (slug, department.id)
            department.slug = slug
            department.save()


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_auto_20170303_1553'),
    ]

    operations = [
        migrations.RunPython(assign_slug),
    ]
