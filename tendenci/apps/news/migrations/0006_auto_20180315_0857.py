# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_auto_20160701_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='meta',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='meta.Meta'),
        ),
        migrations.AlterField(
            model_name='news',
            name='thumbnail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to='news.NewsImage', help_text='The thumbnail image can be used on your homepage or sidebar if it is setup in your theme. The thumbnail image will not display on the news page.', null=True),
        ),
    ]
