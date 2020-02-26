# -*- coding: utf-8 -*-


from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Export',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_label', models.CharField(max_length=50)),
                ('model_name', models.CharField(max_length=50)),
                ('status', models.CharField(default='pending', max_length=50, verbose_name='status', choices=[('completed', 'Completed'), ('pending', 'Pending'), ('failed', 'Failed')])),
                ('result', picklefield.fields.PickledObjectField(default=None, null=True, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_done', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
