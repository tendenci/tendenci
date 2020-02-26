# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0001_initial'),
        ('corporate_memberships', '0011_auto_20171201_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpmembershipapp',
            name='parent_entities',
            field=models.ManyToManyField(help_text='Specify a list of parent entities to select.', to='entities.Entity', verbose_name='Parent Entities', blank=True),
        ),
    ]
