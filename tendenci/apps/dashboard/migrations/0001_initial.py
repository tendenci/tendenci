# -*- coding: utf-8 -*-
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
            ('event_logs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField()),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('-create_dt',),
            },
        ),
        migrations.CreateModel(
            name='DashboardStatType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=0, null=True, verbose_name='Position', blank=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('displayed', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('position',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='dashboardstat',
            name='key',
            field=models.ForeignKey(to='dashboard.DashboardStatType', on_delete=django.db.models.deletion.CASCADE),
        ),
    ]
