

from django.db import migrations
import timezone_field.fields
from tendenci.apps.base.utils import get_timezone_choices


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_auto_20180315_0857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(choices=get_timezone_choices(), verbose_name='Time Zone', default='US/Central', max_length=100),
        ),
    ]
