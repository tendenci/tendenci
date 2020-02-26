# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('forums', '0006_auto_20151115_1335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='language',
            field=models.CharField(default=settings.LANGUAGE_CODE, max_length=10, verbose_name='Language', blank=True, choices=settings.LANGUAGES),
        ),
        migrations.AlterField(
            model_name='topic',
            name='user',
            field=models.ForeignKey(verbose_name='Owner', to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE),
        ),
    ]
