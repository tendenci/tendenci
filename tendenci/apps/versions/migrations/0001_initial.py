# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_dt', models.DateTimeField(verbose_name='create time')),
                ('object_id', models.IntegerField(verbose_name='object id')),
                ('object_repr', models.CharField(max_length=200, verbose_name='object repr')),
                ('object_changes', models.TextField(verbose_name='change message', blank=True)),
                ('object_value', models.TextField(verbose_name='changed object', blank=True)),
                ('hash', models.CharField(default='', max_length=40, null=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=django.db.models.deletion.CASCADE)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
