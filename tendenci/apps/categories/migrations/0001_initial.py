# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='CategoryItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('category', models.ForeignKey(related_name='categoryitem_category', blank=True, to='categories.Category', null=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('parent', models.ForeignKey(related_name='categoryitem_parent', blank=True, to='categories.Category', null=True)),
            ],
        ),
    ]
