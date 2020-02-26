# -*- coding: utf-8 -*-


from django.db import models, migrations
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
            name='Testimonial',
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
                ('first_name', models.CharField(default='', max_length=50, blank=True)),
                ('last_name', models.CharField(default='', max_length=50, blank=True)),
                ('city', models.CharField(default='', max_length=50, blank=True)),
                ('state', models.CharField(default='', max_length=25, blank=True)),
                ('country', models.CharField(default='', max_length=50, blank=True)),
                ('email', models.EmailField(default='', max_length=75, blank=True)),
                ('company', models.CharField(default='', max_length=75, blank=True)),
                ('title', models.CharField(default='', max_length=50, blank=True)),
                ('website', models.URLField(max_length=255, null=True, blank=True)),
                ('testimonial', models.TextField(help_text='Supports &lt;strong&gt;, &lt;em&gt;, and &lt;a&gt; HTML tags.')),
                ('tags', tagging.fields.TagField(help_text='Tags separated by commas. E.g Tag1, Tag2, Tag3', max_length=255, blank=True)),
                ('creator', models.ForeignKey(related_name='testimonials_testimonial_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='testimonials_testimonial_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
            ],
            options={
                'verbose_name': 'Testimonial',
                'verbose_name_plural': 'Testimonials',
            },
        ),
        migrations.CreateModel(
            name='TestimonialPhoto',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, on_delete=django.db.models.deletion.CASCADE, to='files.File')),
            ],
            options={
                'abstract': False,
            },
            bases=('files.file',),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='image',
            field=models.ForeignKey(default=None, to='testimonials.TestimonialPhoto', help_text='Photo for this testimonial.', null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='owner',
            field=models.ForeignKey(related_name='testimonials_testimonial_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
