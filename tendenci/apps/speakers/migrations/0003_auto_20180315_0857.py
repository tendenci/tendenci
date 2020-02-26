# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('speakers', '0002_auto_20150827_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='speaker',
            name='track',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='speakers.Track', null=True),
        ),
    ]
