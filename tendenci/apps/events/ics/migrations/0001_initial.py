# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ICS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_label', models.CharField(max_length=50)),
                ('model_name', models.CharField(max_length=50)),
                ('status', models.CharField(default='pending', max_length=50, verbose_name='status', choices=[('completed', 'Completed'), ('pending', 'Pending'), ('failed', 'Failed')])),
                ('result', picklefield.fields.PickledObjectField(default=None, null=True, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_done', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'ics',
            },
        ),
    ]
