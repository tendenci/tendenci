# -*- coding: utf-8 -*-
from django.db import migrations
import timezone_field.fields
from tendenci.apps.base.utils import get_timezone_choices


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0002_auto_20150804_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(choices=get_timezone_choices(), verbose_name='Time Zone', default='US/Central', max_length=100),
        ),
    ]
