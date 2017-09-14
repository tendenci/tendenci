# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.template.defaultfilters import slugify


def migrate_categories_data(apps, schema_editor):
    from tendenci.apps.jobs.models import Job
    from tendenci.apps.jobs.models import Category as JobCategory
    #Job = apps.get_model("jobs", "Job")
    #JobCategory = apps.get_model("jobs", "Category")
    for job in Job.objects.all():
        job_cat, job_sub_cat = None, None
        cat_items = job.categories.all().order_by('category')
        for cat_item in cat_items:
            if cat_item.category:
                # category
                cat_name = cat_item.category.name
                if cat_name:
                    [job_cat] = JobCategory.objects.filter(name=cat_name,
                                                         parent__isnull=True)[:1] or [None]
                    if not job_cat:
                        job_cat = JobCategory(name=cat_name, slug=slugify(cat_name))
                        job_cat.save()
            elif cat_item.parent:
                # sub category
                sub_cat_name = cat_item.parent.name
                if sub_cat_name:
                    [job_sub_cat] = JobCategory.objects.filter(name=sub_cat_name,
                                                         parent=job_cat)[:1] or [None]
                    if not job_sub_cat:
                        job_sub_cat = JobCategory(name=sub_cat_name, slug=(sub_cat_name))
                        job_sub_cat.parent = job_cat
                        job_sub_cat.save()
        if job_cat:
            job.cat = job_cat
            if job_sub_cat:
                job.sub_cat = job_sub_cat
            job.save(log=False)


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_auto_20170910_1701'),
    ]

    operations = [
        migrations.RunPython(migrate_categories_data),
    ]
