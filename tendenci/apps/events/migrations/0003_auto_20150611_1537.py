# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tendenci.apps.user_groups.utils
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0001_initial'),
        ('events', '0002_auto_20150611_1537'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_groups', '0001_initial'),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='regconfpricing',
            name='groups',
            field=models.ManyToManyField(to='user_groups.Group', blank=True),
        ),
        migrations.AddField(
            model_name='regconfpricing',
            name='reg_conf',
            field=models.ForeignKey(blank=True, to='events.RegistrationConfiguration', null=True),
        ),
        migrations.AddField(
            model_name='regconfpricing',
            name='reg_form',
            field=models.ForeignKey(related_name='regconfpricings', blank=True, to='events.CustomRegForm', help_text="You'll have the chance to edit the selected form", null=True, verbose_name='Custom Registration Form'),
        ),
        migrations.AddField(
            model_name='regaddonoption',
            name='option',
            field=models.ForeignKey(to='events.AddonOption'),
        ),
        migrations.AddField(
            model_name='regaddonoption',
            name='regaddon',
            field=models.ForeignKey(to='events.RegAddon'),
        ),
        migrations.AddField(
            model_name='regaddon',
            name='addon',
            field=models.ForeignKey(to='events.Addon'),
        ),
        migrations.AddField(
            model_name='regaddon',
            name='registration',
            field=models.ForeignKey(to='events.Registration'),
        ),
        migrations.AddField(
            model_name='payment',
            name='registration',
            field=models.OneToOneField(to='events.Registration'),
        ),
        migrations.AddField(
            model_name='organizer',
            name='event',
            field=models.ManyToManyField(to='events.Event', blank=True),
        ),
        migrations.AddField(
            model_name='organizer',
            name='user',
            field=models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='creator',
            field=models.ForeignKey(related_name='events_event_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='entity',
            field=models.ForeignKey(related_name='events_event_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=tendenci.apps.user_groups.utils.get_default_group, to='user_groups.Group', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='image',
            field=models.ForeignKey(blank=True, to='events.EventPhoto', help_text='Photo that represents this event.', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='meta',
            field=models.OneToOneField(null=True, to='meta.Meta'),
        ),
        migrations.AddField(
            model_name='event',
            name='owner',
            field=models.ForeignKey(related_name='events_event_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='place',
            field=models.ForeignKey(to='events.Place', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='recurring_event',
            field=models.ForeignKey(to='events.RecurringEvent', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='registration_configuration',
            field=models.OneToOneField(null=True, editable=False, to='events.RegistrationConfiguration'),
        ),
        migrations.AddField(
            model_name='event',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='events.Type', null=True),
        ),
        migrations.AddField(
            model_name='discount',
            name='event',
            field=models.ForeignKey(to='events.Event'),
        ),
        migrations.AddField(
            model_name='customregformentry',
            name='form',
            field=models.ForeignKey(related_name='entries', to='events.CustomRegForm'),
        ),
        migrations.AddField(
            model_name='customregform',
            name='creator',
            field=models.ForeignKey(related_name='custom_reg_creator', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='customregform',
            name='owner',
            field=models.ForeignKey(related_name='custom_reg_owner', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='customregfieldentry',
            name='entry',
            field=models.ForeignKey(related_name='field_entries', to='events.CustomRegFormEntry'),
        ),
        migrations.AddField(
            model_name='customregfieldentry',
            name='field',
            field=models.ForeignKey(related_name='entries', to='events.CustomRegField'),
        ),
        migrations.AddField(
            model_name='customregfield',
            name='form',
            field=models.ForeignKey(related_name='fields', to='events.CustomRegForm'),
        ),
        migrations.AddField(
            model_name='addonoption',
            name='addon',
            field=models.ForeignKey(related_name='options', to='events.Addon'),
        ),
        migrations.AddField(
            model_name='addon',
            name='event',
            field=models.ForeignKey(to='events.Event'),
        ),
        migrations.AddField(
            model_name='addon',
            name='group',
            field=models.ForeignKey(blank=True, to='user_groups.Group', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='regaddonoption',
            unique_together=set([('regaddon', 'option')]),
        ),
    ]
