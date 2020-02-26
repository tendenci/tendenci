# -*- coding: utf-8 -*-


from django.db import models, migrations
import tendenci.apps.user_groups.utils
import tendenci.apps.base.fields
import django.db.models.deletion
import tendenci.libs.tinymce.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpFileMigration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('t4_id', models.IntegerField()),
                ('t5_id', models.IntegerField()),
            ],
            options={
                'db_table': 'mig_help_files_helpfile_t4_to_t5',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='HelpFile',
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
                ('slug', tendenci.apps.base.fields.SlugField(unique=True, max_length=100, verbose_name='URL Path', db_index=True)),
                ('question', models.CharField(max_length=500)),
                ('answer', tendenci.libs.tinymce.models.HTMLField()),
                ('level', models.CharField(default='basic', max_length=100, choices=[('basic', 'basic'), ('intermediate', 'intermediate'), ('advanced', 'advanced'), ('expert', 'expert')])),
                ('is_faq', models.BooleanField(default=False)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_video', models.BooleanField(default=False)),
                ('syndicate', models.BooleanField(default=True, verbose_name='Include in RSS feed')),
                ('view_totals', models.PositiveIntegerField(default=0)),
                ('creator', models.ForeignKey(related_name='help_files_helpfile_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='help_files_helpfile_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=tendenci.apps.user_groups.utils.get_default_group, to='user_groups.Group', null=True)),
                ('owner', models.ForeignKey(related_name='help_files_helpfile_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.AddField(
            model_name='helpfile',
            name='topics',
            field=models.ManyToManyField(to='help_files.Topic'),
        ),
    ]
