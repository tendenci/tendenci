# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
import tendenci.apps.files.models


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        ('emails', '0001_initial'),
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=255, null=True, blank=True)),
                ('actiontype', models.CharField(default='Distribution E-mail', max_length=30, choices=[('Distribution E-mail', 'Distribution E-mail'), ('Direct Mail Letter', 'Direct Mail Letter'), ('Phone Call', 'Phone Call'), ('Press Release', 'Press Release'), ('Direct Mail Post Card', 'Direct Mail Post Card'), ('Newspaper Advertisement', 'Newspaper Advertisement'), ('Favorable Newspaper Article', 'Favorable Newspaper Article'), ('Unfavorable Newspaper Article', 'Unfavorable Newspaper Article')])),
                ('actionname', models.CharField(max_length=255, null=True, blank=True)),
                ('member_only', models.BooleanField(default=False)),
                ('send_to_email2', models.BooleanField(default=False)),
                ('include_login', models.BooleanField()),
                ('personalize_subject_first_name', models.BooleanField()),
                ('personalize_subject_last_name', models.BooleanField()),
                ('jump_links', models.IntegerField(default=1, choices=[(1, 'Include'), (0, 'Skip')])),
                ('events', models.IntegerField(default=1, choices=[(1, 'Include'), (0, 'Skip')])),
                ('event_start_dt', models.DateField()),
                ('event_end_dt', models.DateField()),
                ('events_type', models.IntegerField(default=1, null=True, blank=True)),
                ('articles', models.IntegerField(default=1, choices=[(1, 'Include'), (0, 'Skip')])),
                ('articles_days', models.IntegerField(default=60, choices=[(1, '1'), (3, '3'), (5, '5'), (7, '7'), (14, '14'), (30, '30'), (60, '60'), (90, '90'), (120, '120'), (0, 'ALL')])),
                ('news', models.IntegerField(default=1, choices=[(1, 'Include'), (0, 'Skip')])),
                ('news_days', models.IntegerField(default=30, choices=[(1, '1'), (3, '3'), (5, '5'), (7, '7'), (14, '14'), (30, '30'), (60, '60'), (90, '90'), (120, '120'), (0, 'ALL')])),
                ('jobs', models.IntegerField(default=1, choices=[(1, 'Include'), (0, 'Skip')])),
                ('jobs_days', models.IntegerField(default=30, choices=[(1, '1'), (3, '3'), (5, '5'), (7, '7'), (14, '14'), (30, '30'), (60, '60'), (90, '90'), (120, '120'), (0, 'ALL')])),
                ('pages', models.IntegerField(default=0, choices=[(1, 'Include'), (0, 'Skip')])),
                ('pages_days', models.IntegerField(default=7, choices=[(1, '1'), (3, '3'), (5, '5'), (7, '7'), (14, '14'), (30, '30'), (60, '60'), (90, '90'), (120, '120'), (0, 'ALL')])),
                ('directories', models.IntegerField(default=0, choices=[(1, 'Include'), (0, 'Skip')])),
                ('directories_days', models.IntegerField(default=7, choices=[(1, '1'), (3, '3'), (5, '5'), (7, '7'), (14, '14'), (30, '30'), (60, '60'), (90, '90'), (120, '120'), (0, 'ALL')])),
                ('resumes', models.IntegerField(default=0, choices=[(1, 'Include'), (0, 'Skip')])),
                ('resumes_days', models.IntegerField(default=7, choices=[(1, '1'), (3, '3'), (5, '5'), (7, '7'), (14, '14'), (30, '30'), (60, '60'), (90, '90'), (120, '120'), (0, 'ALL')])),
                ('default_template', models.CharField(max_length=255, null=True)),
                ('format', models.IntegerField(default=0, choices=[(1, 'Detailed - original format View Example'), (0, 'Simplified - removes AUTHOR, POSTED BY, RELEASES DATE, etc from the detailed format View Example')])),
                ('sla', models.BooleanField(default=False)),
                ('send_status', models.CharField(default='draft', max_length=30, choices=[('draft', 'Draft'), ('queued', 'Queued'), ('sending', 'Sending'), ('sent', 'Sent'), ('resending', 'Resending'), ('resent', 'Resent')])),
                ('date_created', models.DateTimeField(null=True, blank=True)),
                ('date_submitted', models.DateTimeField(null=True, blank=True)),
                ('date_email_sent', models.DateTimeField(null=True, blank=True)),
                ('date_last_resent', models.DateTimeField(null=True, blank=True)),
                ('email_sent_count', models.IntegerField(default=0, null=True, blank=True)),
                ('resend_count', models.IntegerField(default=0, null=True, blank=True)),
                ('security_key', models.CharField(max_length=50, null=True, blank=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='articles.Article', null=True)),
                ('email', models.ForeignKey(to='emails.Email', null=True, on_delete=django.db.models.deletion.CASCADE)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='user_groups.Group', null=True)),
            ],
            options={
                'verbose_name': 'Newsletter',
                'verbose_name_plural': 'Newsletters',
            },
        ),
        migrations.CreateModel(
            name='NewsletterTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('template_id', models.CharField(max_length=100, unique=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('html_file', models.FileField(null=True, upload_to=tendenci.apps.files.models.file_directory)),
                ('zip_file', models.FileField(null=True, upload_to=tendenci.apps.files.models.file_directory)),
            ],
            options={
            },
        ),
    ]
