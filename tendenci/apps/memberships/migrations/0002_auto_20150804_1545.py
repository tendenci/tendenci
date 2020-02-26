# -*- coding: utf-8 -*-


from django.db import models, migrations
import tendenci.apps.memberships.models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershipimport',
            name='recap_file',
            field=models.FileField(max_length=260, null=True, verbose_name='Recap File', upload_to=''),
        ),
        migrations.AlterField(
            model_name='membershipimport',
            name='upload_file',
            field=models.FileField(max_length=260, null=True, verbose_name='Upload File', upload_to=tendenci.apps.memberships.models.get_import_file_path),
        ),
    ]
