# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='video_embed_url',
            field=models.URLField(null=True, verbose_name='Embed URL', blank=True),
        ),
    ]
