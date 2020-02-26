# -*- coding: utf-8 -*-


from django.db import migrations
from django.template.defaultfilters import slugify


def assign_slug(apps, schema_editor):
    """
        Assign value to the slug field if slug is blank for locations
    """
    Location = apps.get_model('locations', 'Location')
    for location in Location.objects.all():
        if not location.slug:
            slug = slugify(location.location_name)
            if Location.objects.filter(slug=slug).exists():
                slug = '%s%s' % (slug, location.id)
            location.slug = slug
            location.save()

class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(assign_slug),
    ]
