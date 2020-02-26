# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='Documents',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, on_delete=django.db.models.deletion.CASCADE, to='files.File')),
                ('other', models.CharField(max_length=200, verbose_name='other', blank=True)),
                ('document_dt', models.DateField(null=True, verbose_name='Document Date', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('files.file',),
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=300, verbose_name='type')),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, on_delete=django.db.models.deletion.CASCADE, to='files.File')),
                ('title', models.CharField(max_length=200, verbose_name='title', blank=True)),
                ('photo_description', models.TextField(null=True, verbose_name='Photo Description', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('files.file',),
        ),
        migrations.CreateModel(
            name='Project',
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
                ('tags', tagging.fields.TagField(help_text='Tag 1, Tag 2, ...', max_length=255, blank=True)),
                ('slug', models.SlugField(unique=True, max_length=200, verbose_name='URL Path')),
                ('project_name', models.CharField(max_length=300, verbose_name='Project Name')),
                ('project_status', models.CharField(blank=True, max_length=50, verbose_name='Project Status', choices=[('open', 'Open'), ('assigned', 'Assigned'), ('in progress', 'In Progress'), ('pending', 'Pending'), ('closed', 'Closed')])),
                ('cost', models.DecimalField(null=True, verbose_name='Project Cost', max_digits=10, decimal_places=2, blank=True)),
                ('location', models.CharField(max_length=200, null=True, verbose_name='Location', blank=True)),
                ('city', models.CharField(max_length=200, null=True, verbose_name='City', blank=True)),
                ('state', models.CharField(max_length=300, null=True, verbose_name='State', blank=True)),
                ('start_dt', models.DateField(null=True, verbose_name='Project Start', blank=True)),
                ('end_dt', models.DateField(null=True, verbose_name='Project End', blank=True)),
                ('resolution', models.TextField(verbose_name='Resolution', blank=True)),
                ('project_description', models.TextField(verbose_name='Project Description', blank=True)),
                ('website_title', models.CharField(max_length=200, verbose_name='Project Website Title', blank=True)),
                ('website_url', models.URLField(verbose_name='Project Website URL', blank=True)),
                ('video_embed_code', models.TextField(verbose_name='Video Embed Code', blank=True)),
                ('video_title', models.CharField(max_length=200, verbose_name='Video Title', blank=True)),
                ('video_description', models.TextField(verbose_name='Video Description', blank=True)),
                ('client', models.ForeignKey(blank=True, to='projects.ClientList', null=True, on_delete=django.db.models.deletion.CASCADE)),
                ('creator', models.ForeignKey(related_name='projects_project_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='projects_project_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('owner', models.ForeignKey(related_name='projects_project_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
        ),
        migrations.CreateModel(
            name='ProjectManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=200, verbose_name='First Name', blank=True)),
                ('last_name', models.CharField(max_length=200, verbose_name='Last Name', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(unique=True, max_length=200, verbose_name='number')),
            ],
        ),
        migrations.CreateModel(
            name='TeamMembers',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, on_delete=django.db.models.deletion.CASCADE, to='files.File')),
                ('first_name', models.CharField(max_length=200, verbose_name='First Name', blank=True)),
                ('last_name', models.CharField(max_length=200, verbose_name='Last Name', blank=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title', blank=True)),
                ('role', models.CharField(max_length=200, verbose_name='Role', blank=True)),
                ('team_description', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('project', models.ForeignKey(related_name='projects_teammembers_related', to='projects.Project', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('files.file',),
        ),
        migrations.AddField(
            model_name='project',
            name='project_manager',
            field=models.ForeignKey(blank=True, to='projects.ProjectManager', null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='project',
            name='project_number',
            field=models.ForeignKey(null=True, blank=True, to='projects.ProjectNumber', unique=True, on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='photo',
            name='project',
            field=models.ForeignKey(related_name='projects_photo_related', to='projects.Project', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='documents',
            name='project',
            field=models.ForeignKey(related_name='projects_documents_related', to='projects.Project', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='documents',
            name='type',
            field=models.ForeignKey(to='projects.DocumentType', blank=True, on_delete=django.db.models.deletion.CASCADE),
        ),
    ]
