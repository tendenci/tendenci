# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import tendenci.libs.tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allow_anonymous_view', models.BooleanField(default=True, verbose_name='Public can view')),
                ('allow_user_view', models.BooleanField(default=True, verbose_name='Signed in user can view')),
                ('allow_member_view', models.BooleanField(default=True)),
                ('allow_user_edit', models.BooleanField(default=False, verbose_name='Signed in user can change')),
                ('allow_member_edit', models.BooleanField(default=False)),
                ('create_dt', models.DateTimeField(auto_now_add=True, verbose_name='Created On')),
                ('update_dt', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('creator_username', models.CharField(max_length=50)),
                ('owner_username', models.CharField(max_length=50)),
                ('status', models.BooleanField(default=True, verbose_name='Active')),
                ('status_detail', models.CharField(default='active', max_length=50)),
                ('guid', models.CharField(max_length=50)),
                ('priority', models.IntegerField(default=0)),
                ('subject', models.CharField(max_length=255)),
                ('body', tendenci.libs.tinymce.models.HTMLField()),
                ('sender', models.CharField(max_length=255)),
                ('sender_display', models.CharField(max_length=255)),
                ('reply_to', models.CharField(max_length=255)),
                ('recipient', models.CharField(default='', max_length=255, blank=True)),
                ('recipient_dispaly', models.CharField(default='', max_length=255, blank=True)),
                ('recipient_cc', models.CharField(default='', max_length=255, blank=True)),
                ('recipient_cc_display', models.CharField(default='', max_length=255, blank=True)),
                ('recipient_bcc', models.CharField(default='', max_length=255, blank=True)),
                ('attachments', models.CharField(default='', max_length=500, blank=True)),
                ('content_type', models.CharField(default='text/html', max_length=255, choices=[('text/html', 'text/html'), ('text', 'text')])),
                ('creator', models.ForeignKey(related_name='emails_email_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='emails_email_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('owner', models.ForeignKey(related_name='emails_email_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
