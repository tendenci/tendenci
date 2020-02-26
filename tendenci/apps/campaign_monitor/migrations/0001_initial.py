# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import tendenci.apps.files.models


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('campaign_id', models.CharField(unique=True, max_length=100)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default='D', max_length=1, choices=[('S', 'Sent'), ('C', 'Scheduled'), ('D', 'Draft')])),
                ('name', models.CharField(max_length=100)),
                ('subject', models.CharField(max_length=500)),
                ('sent_date', models.DateTimeField(null=True, blank=True)),
                ('web_version_url', models.URLField(null=True, blank=True)),
                ('total_recipients', models.IntegerField(default=0)),
                ('scheduled_date', models.DateTimeField(null=True, blank=True)),
                ('scheduled_time_zone', models.CharField(max_length=100, null=True, blank=True)),
                ('preview_url', models.URLField(null=True, blank=True)),
                ('from_name', models.CharField(max_length=100, null=True, blank=True)),
                ('from_email', models.EmailField(max_length=254, null=True, blank=True)),
                ('reply_to', models.EmailField(max_length=254, null=True, blank=True)),
            ],
            options={
            },
        ),
        migrations.CreateModel(
            name='GroupQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(to='user_groups.Group', on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='ListMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('list_id', models.CharField(max_length=100)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('last_sync_dt', models.DateTimeField(null=True)),
                ('group', models.ForeignKey(to='user_groups.Group', on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriberQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(to='user_groups.Group', on_delete=django.db.models.deletion.CASCADE)),
                ('subscriber', models.ForeignKey(to='forms.FormEntry', null=True, on_delete=django.db.models.deletion.CASCADE)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('template_id', models.CharField(max_length=100, unique=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('cm_preview_url', models.URLField(null=True)),
                ('cm_screenshot_url', models.URLField(null=True)),
                ('html_file', models.FileField(null=True, upload_to=tendenci.apps.files.models.file_directory)),
                ('zip_file', models.FileField(null=True, upload_to=tendenci.apps.files.models.file_directory)),
            ],
            options={
            },
        ),
        migrations.AddField(
            model_name='campaign',
            name='lists',
            field=models.ManyToManyField(to='campaign_monitor.ListMap'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='template',
            field=models.ForeignKey(blank=True, to='campaign_monitor.Template', null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
    ]
