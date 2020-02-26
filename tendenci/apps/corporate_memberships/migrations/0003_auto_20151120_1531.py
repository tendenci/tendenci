# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporate_memberships', '0002_auto_20150804_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporatemembershiptype',
            name='apply_cap',
            field=models.BooleanField(default=False, help_text='If checked, specify the membership cap below.', verbose_name='Apply cap'),
        ),
        migrations.AddField(
            model_name='corporatemembershiptype',
            name='membership_cap',
            field=models.IntegerField(default=0, help_text='The maximum number of employees allowed.', null=True, verbose_name='Membership cap', blank=True),
        ),
    ]
