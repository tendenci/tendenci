# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChecklistItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=0, null=True, verbose_name='Position', blank=True)),
                ('key', models.CharField(unique=True, max_length=20)),
                ('label', models.CharField(max_length=200)),
                ('done', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('position',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UpdateTracker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_updating', models.BooleanField(default=False)),
            ],
        ),
    ]
