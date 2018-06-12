# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testimonials', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='testimonial',
            options={'ordering': ['position'], 'verbose_name': 'Testimonial', 'verbose_name_plural': 'Testimonials', 'permissions': (('view_testimonial', 'Can view testimonial'),)},
        ),
        migrations.AddField(
            model_name='testimonial',
            name='position',
            field=models.IntegerField(default=0, null=True, verbose_name='Position', blank=True),
        ),
    ]
