# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.template.defaultfilters import slugify


def migrate_categories_data(apps, schema_editor):
    from tendenci.apps.directories.models import Directory
    from tendenci.apps.directories.models import Category as DirectoryCategory

    for directory in Directory.objects.all():
        directory_cat, directory_sub_cat = None, None
        cat_items = directory.categories.all().order_by('category')
        for cat_item in cat_items:
            if cat_item.category:
                # category
                cat_name = cat_item.category.name
                if cat_name:
                    [directory_cat] = DirectoryCategory.objects.filter(name=cat_name,
                                                         parent__isnull=True)[:1] or [None]
                    if not directory_cat:
                        directory_cat = DirectoryCategory(name=cat_name, slug=slugify(cat_name))
                        directory_cat.save()
            elif cat_item.parent:
                # sub category
                sub_cat_name = cat_item.parent.name
                if sub_cat_name:
                    [directory_sub_cat] = DirectoryCategory.objects.filter(name=sub_cat_name,
                                                         parent=directory_cat)[:1] or [None]
                    if not directory_sub_cat:
                        directory_sub_cat = DirectoryCategory(name=sub_cat_name, slug=(sub_cat_name))
                        directory_sub_cat.parent = directory_cat
                        directory_sub_cat.save()
        if directory_cat:
            directory.cat = directory_cat
            if directory_sub_cat:
                directory.sub_cat = directory_sub_cat
            directory.save(log=False)

class Migration(migrations.Migration):

    dependencies = [
        ('directories', '0004_auto_20171013_1043'),
    ]

    operations = [
        migrations.RunPython(migrate_categories_data),
    ]
