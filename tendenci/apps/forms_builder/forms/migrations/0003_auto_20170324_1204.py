# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
import tendenci.apps.user_groups.utils


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        ('site_settings', '0001_initial'),
        ('search', '0001_initial'),
        ('forms', '0002_auto_20161208_2003'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to='user_groups.Group', null=True),
        ),
    ]
