# -*- coding: utf-8 -*-


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='Email',
            old_name='recipient_dispaly',
            new_name='recipient_display',
        ),
    ]
