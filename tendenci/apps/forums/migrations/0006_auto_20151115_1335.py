# -*- coding: utf-8 -*-


from django.db import migrations, models
import datetime
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
        ('forums', '0005_auto_20151009_1754'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['position'], 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AddField(
            model_name='category',
            name='allow_anonymous_view',
            field=models.BooleanField(default=True, verbose_name='Public can view'),
        ),
        migrations.AddField(
            model_name='category',
            name='allow_member_edit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='category',
            name='allow_member_view',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='category',
            name='allow_user_edit',
            field=models.BooleanField(default=False, verbose_name='Signed in user can change'),
        ),
        migrations.AddField(
            model_name='category',
            name='allow_user_view',
            field=models.BooleanField(default=True, verbose_name='Signed in user can view'),
        ),
        migrations.AddField(
            model_name='category',
            name='create_dt',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 15, 13, 34, 38, 95900), verbose_name='Created On', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='creator',
            field=models.ForeignKey(related_name='forums_category_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='creator_username',
            field=models.CharField(default='admin', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='entity',
            field=models.ForeignKey(related_name='forums_category_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='owner',
            field=models.ForeignKey(related_name='forums_category_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='owner_username',
            field=models.CharField(default='admin', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='status',
            field=models.BooleanField(default=True, verbose_name='Active'),
        ),
        migrations.AddField(
            model_name='category',
            name='status_detail',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.AddField(
            model_name='category',
            name='update_dt',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 15, 13, 35, 8, 338867), verbose_name='Last Updated', auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='category',
            name='hidden',
            field=models.BooleanField(default=False, help_text='If checked, this category will be visible only for staff and the rest of the permissions below will be ignored', verbose_name='Hidden'),
        ),
    ]
