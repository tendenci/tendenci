# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'RegConfPricing.status'
        db.alter_column(u'events_regconfpricing', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegConfPricing.include_tax'
        db.alter_column(u'events_regconfpricing', 'include_tax', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegConfPricing.allow_anonymous'
        db.alter_column(u'events_regconfpricing', 'allow_anonymous', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegConfPricing.allow_user'
        db.alter_column(u'events_regconfpricing', 'allow_user', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegConfPricing.allow_member'
        db.alter_column(u'events_regconfpricing', 'allow_member', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegField.required'
        db.alter_column(u'events_customregfield', 'required', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegField.visible'
        db.alter_column(u'events_customregfield', 'visible', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegField.display_on_roster'
        db.alter_column(u'events_customregfield', 'display_on_roster', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Registrant.checked_in'
        db.alter_column(u'events_registrant', 'checked_in', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Registrant.use_free_pass'
        db.alter_column(u'events_registrant', 'use_free_pass', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Registrant.override'
        db.alter_column(u'events_registrant', 'override', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Registrant.reminder'
        db.alter_column(u'events_registrant', 'reminder', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Registrant.is_primary'
        db.alter_column(u'events_registrant', 'is_primary', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.last_name'
        db.alter_column(u'events_customregform', 'last_name', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.position_title'
        db.alter_column(u'events_customregform', 'position_title', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.mail_name'
        db.alter_column(u'events_customregform', 'mail_name', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.city'
        db.alter_column(u'events_customregform', 'city', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.zip'
        db.alter_column(u'events_customregform', 'zip', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.comments'
        db.alter_column(u'events_customregform', 'comments', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.state'
        db.alter_column(u'events_customregform', 'state', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.company_name'
        db.alter_column(u'events_customregform', 'company_name', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.email'
        db.alter_column(u'events_customregform', 'email', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.meal_option'
        db.alter_column(u'events_customregform', 'meal_option', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.first_name'
        db.alter_column(u'events_customregform', 'first_name', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.phone'
        db.alter_column(u'events_customregform', 'phone', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.address'
        db.alter_column(u'events_customregform', 'address', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CustomRegForm.country'
        db.alter_column(u'events_customregform', 'country', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegistrationConfiguration.display_registration_stats'
        db.alter_column(u'events_registrationconfiguration', 'display_registration_stats', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegistrationConfiguration.use_custom_reg_form'
        db.alter_column(u'events_registrationconfiguration', 'use_custom_reg_form', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegistrationConfiguration.send_reminder'
        db.alter_column(u'events_registrationconfiguration', 'send_reminder', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegistrationConfiguration.payment_required'
        db.alter_column(u'events_registrationconfiguration', 'payment_required', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegistrationConfiguration.enabled'
        db.alter_column(u'events_registrationconfiguration', 'enabled', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegistrationConfiguration.bind_reg_form_to_conf_only'
        db.alter_column(u'events_registrationconfiguration', 'bind_reg_form_to_conf_only', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegistrationConfiguration.is_guest_price'
        db.alter_column(u'events_registrationconfiguration', 'is_guest_price', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegistrationConfiguration.allow_free_pass'
        db.alter_column(u'events_registrationconfiguration', 'allow_free_pass', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegistrationConfiguration.discount_eligible'
        db.alter_column(u'events_registrationconfiguration', 'discount_eligible', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RegistrationConfiguration.require_guests_info'
        db.alter_column(u'events_registrationconfiguration', 'require_guests_info', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.is_recurring_event'
        db.alter_column(u'events_event', 'is_recurring_event', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.allow_user_view'
        db.alter_column(u'events_event', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.on_weekend'
        db.alter_column(u'events_event', 'on_weekend', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.priority'
        db.alter_column(u'events_event', 'priority', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.enable_private_slug'
        db.alter_column(u'events_event', 'enable_private_slug', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.allow_anonymous_view'
        db.alter_column(u'events_event', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.status'
        db.alter_column(u'events_event', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.display_event_registrants'
        db.alter_column(u'events_event', 'display_event_registrants', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.all_day'
        db.alter_column(u'events_event', 'all_day', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.allow_user_edit'
        db.alter_column(u'events_event', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.mark_registration_ended'
        db.alter_column(u'events_event', 'mark_registration_ended', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.allow_member_view'
        db.alter_column(u'events_event', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Event.allow_member_edit'
        db.alter_column(u'events_event', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Speaker.featured'
        db.alter_column(u'events_speaker', 'featured', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Addon.status'
        db.alter_column(u'events_addon', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Addon.allow_anonymous'
        db.alter_column(u'events_addon', 'allow_anonymous', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Addon.allow_user'
        db.alter_column(u'events_addon', 'allow_user', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Addon.allow_member'
        db.alter_column(u'events_addon', 'allow_member', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Registration.override_table'
        db.alter_column(u'events_registration', 'override_table', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Registration.is_table'
        db.alter_column(u'events_registration', 'is_table', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Registration.canceled'
        db.alter_column(u'events_registration', 'canceled', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Registration.reminder'
        db.alter_column(u'events_registration', 'reminder', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'RegConfPricing.status'
        db.alter_column(u'events_regconfpricing', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegConfPricing.include_tax'
        db.alter_column(u'events_regconfpricing', 'include_tax', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegConfPricing.allow_anonymous'
        db.alter_column(u'events_regconfpricing', 'allow_anonymous', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegConfPricing.allow_user'
        db.alter_column(u'events_regconfpricing', 'allow_user', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegConfPricing.allow_member'
        db.alter_column(u'events_regconfpricing', 'allow_member', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegField.required'
        db.alter_column(u'events_customregfield', 'required', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegField.visible'
        db.alter_column(u'events_customregfield', 'visible', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegField.display_on_roster'
        db.alter_column(u'events_customregfield', 'display_on_roster', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Registrant.checked_in'
        db.alter_column(u'events_registrant', 'checked_in', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Registrant.use_free_pass'
        db.alter_column(u'events_registrant', 'use_free_pass', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Registrant.override'
        db.alter_column(u'events_registrant', 'override', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Registrant.reminder'
        db.alter_column(u'events_registrant', 'reminder', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Registrant.is_primary'
        db.alter_column(u'events_registrant', 'is_primary', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.last_name'
        db.alter_column(u'events_customregform', 'last_name', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.position_title'
        db.alter_column(u'events_customregform', 'position_title', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.mail_name'
        db.alter_column(u'events_customregform', 'mail_name', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.city'
        db.alter_column(u'events_customregform', 'city', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.zip'
        db.alter_column(u'events_customregform', 'zip', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.comments'
        db.alter_column(u'events_customregform', 'comments', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.state'
        db.alter_column(u'events_customregform', 'state', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.company_name'
        db.alter_column(u'events_customregform', 'company_name', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.email'
        db.alter_column(u'events_customregform', 'email', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.meal_option'
        db.alter_column(u'events_customregform', 'meal_option', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.first_name'
        db.alter_column(u'events_customregform', 'first_name', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.phone'
        db.alter_column(u'events_customregform', 'phone', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.address'
        db.alter_column(u'events_customregform', 'address', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CustomRegForm.country'
        db.alter_column(u'events_customregform', 'country', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegistrationConfiguration.display_registration_stats'
        db.alter_column(u'events_registrationconfiguration', 'display_registration_stats', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegistrationConfiguration.use_custom_reg_form'
        db.alter_column(u'events_registrationconfiguration', 'use_custom_reg_form', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegistrationConfiguration.send_reminder'
        db.alter_column(u'events_registrationconfiguration', 'send_reminder', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegistrationConfiguration.payment_required'
        db.alter_column(u'events_registrationconfiguration', 'payment_required', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegistrationConfiguration.enabled'
        db.alter_column(u'events_registrationconfiguration', 'enabled', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegistrationConfiguration.bind_reg_form_to_conf_only'
        db.alter_column(u'events_registrationconfiguration', 'bind_reg_form_to_conf_only', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegistrationConfiguration.is_guest_price'
        db.alter_column(u'events_registrationconfiguration', 'is_guest_price', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegistrationConfiguration.allow_free_pass'
        db.alter_column(u'events_registrationconfiguration', 'allow_free_pass', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegistrationConfiguration.discount_eligible'
        db.alter_column(u'events_registrationconfiguration', 'discount_eligible', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RegistrationConfiguration.require_guests_info'
        db.alter_column(u'events_registrationconfiguration', 'require_guests_info', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.is_recurring_event'
        db.alter_column(u'events_event', 'is_recurring_event', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.allow_user_view'
        db.alter_column(u'events_event', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.on_weekend'
        db.alter_column(u'events_event', 'on_weekend', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.priority'
        db.alter_column(u'events_event', 'priority', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.enable_private_slug'
        db.alter_column(u'events_event', 'enable_private_slug', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.allow_anonymous_view'
        db.alter_column(u'events_event', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.status'
        db.alter_column(u'events_event', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.display_event_registrants'
        db.alter_column(u'events_event', 'display_event_registrants', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.all_day'
        db.alter_column(u'events_event', 'all_day', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.allow_user_edit'
        db.alter_column(u'events_event', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.mark_registration_ended'
        db.alter_column(u'events_event', 'mark_registration_ended', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.allow_member_view'
        db.alter_column(u'events_event', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Event.allow_member_edit'
        db.alter_column(u'events_event', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Speaker.featured'
        db.alter_column(u'events_speaker', 'featured', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Addon.status'
        db.alter_column(u'events_addon', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Addon.allow_anonymous'
        db.alter_column(u'events_addon', 'allow_anonymous', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Addon.allow_user'
        db.alter_column(u'events_addon', 'allow_user', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Addon.allow_member'
        db.alter_column(u'events_addon', 'allow_member', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Registration.override_table'
        db.alter_column(u'events_registration', 'override_table', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Registration.is_table'
        db.alter_column(u'events_registration', 'is_table', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Registration.canceled'
        db.alter_column(u'events_registration', 'canceled', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Registration.reminder'
        db.alter_column(u'events_registration', 'reminder', self.gf('django.db.models.fields.BooleanField')())

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'emails.email': {
            'Meta': {'object_name': 'Email'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'attachments': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'body': ('tinymce.models.HTMLField', [], {}),
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'text/html'", 'max_length': '255'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'emails_email_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'emails_email_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'emails_email_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'recipient': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'recipient_bcc': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'recipient_cc': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'recipient_cc_display': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'recipient_dispaly': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'reply_to': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sender_display': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'entities.entity': {
            'Meta': {'ordering': "('entity_name',)", 'object_name': 'Entity'},
            'admin_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'allow_anonymous_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'entity_parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entity_children'", 'null': 'True', 'to': u"orm['entities.Entity']"}),
            'entity_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'})
        },
        u'events.addon': {
            'Meta': {'object_name': 'Addon'},
            'allow_anonymous': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Event']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_groups.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'events.addonoption': {
            'Meta': {'object_name': 'AddonOption'},
            'addon': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'options'", 'to': u"orm['events.Addon']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'events.customregfield': {
            'Meta': {'ordering': "('position',)", 'object_name': 'CustomRegField'},
            'choices': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'display_on_roster': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'field_function': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['events.CustomRegForm']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'map_to_field': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'required': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'events.customregfieldentry': {
            'Meta': {'object_name': 'CustomRegFieldEntry'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'field_entries'", 'to': u"orm['events.CustomRegFormEntry']"}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': u"orm['events.CustomRegField']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        },
        u'events.customregform': {
            'Meta': {'object_name': 'CustomRegForm'},
            'address': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'custom_reg_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'mail_name': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'meal_option': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'custom_reg_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'position_title': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'})
        },
        u'events.customregformentry': {
            'Meta': {'object_name': 'CustomRegFormEntry'},
            'entry_time': ('django.db.models.fields.DateTimeField', [], {}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': u"orm['events.CustomRegForm']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'events.discount': {
            'Meta': {'object_name': 'Discount'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'events.event': {
            'Meta': {'object_name': 'Event'},
            'all_day': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'events_event_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'display_event_registrants': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'display_registrants_to': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '6'}),
            'enable_private_slug': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'end_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 9, 0, 0)'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'events_event_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['user_groups.Group']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.EventPhoto']", 'null': 'True', 'blank': 'True'}),
            'is_recurring_event': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'mark_registration_ended': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'meta': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['meta.Meta']", 'unique': 'True', 'null': 'True'}),
            'on_weekend': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'events_event_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Place']", 'null': 'True'}),
            'priority': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'private_slug': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '500', 'blank': 'True'}),
            'recurring_event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.RecurringEvent']", 'null': 'True'}),
            'registration_configuration': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['events.RegistrationConfiguration']", 'unique': 'True', 'null': 'True'}),
            'start_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 9, 0, 0)'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'timezone': ('timezones.fields.TimeZoneField', [], {'default': "'US/Central'", 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Type']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.eventphoto': {
            'Meta': {'object_name': 'EventPhoto', '_ormbases': [u'files.File']},
            u'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['files.File']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'events.organizer': {
            'Meta': {'object_name': 'Organizer'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'event': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['events.Event']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'events.payment': {
            'Meta': {'object_name': 'Payment'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['events.Registration']", 'unique': 'True'})
        },
        u'events.paymentmethod': {
            'Meta': {'object_name': 'PaymentMethod'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'events.place': {
            'Meta': {'object_name': 'Place'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'})
        },
        u'events.recurringevent': {
            'Meta': {'object_name': 'RecurringEvent'},
            'ends_on': ('django.db.models.fields.DateTimeField', [], {}),
            'frequency': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repeat_type': ('django.db.models.fields.IntegerField', [], {}),
            'starts_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 9, 0, 0)'})
        },
        u'events.regaddon': {
            'Meta': {'object_name': 'RegAddon'},
            'addon': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Addon']"}),
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Registration']"}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.regaddonoption': {
            'Meta': {'unique_together': "(('regaddon', 'option'),)", 'object_name': 'RegAddonOption'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.AddonOption']"}),
            'regaddon': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.RegAddon']"})
        },
        u'events.regconfpricing': {
            'Meta': {'ordering': "('position',)", 'object_name': 'RegConfPricing'},
            'allow_anonymous': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 9, 0, 0)'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['user_groups.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_tax': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'payment_required': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'reg_conf': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.RegistrationConfiguration']", 'null': 'True', 'blank': 'True'}),
            'reg_form': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'regconfpricings'", 'null': 'True', 'to': u"orm['events.CustomRegForm']"}),
            'start_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 9, 9, 0, 0)'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '4', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'})
        },
        u'events.registrant': {
            'Meta': {'object_name': 'Registrant'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2', 'blank': 'True'}),
            'cancel_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'checked_in': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'checked_in_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'custom_reg_form_entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'registrants'", 'null': 'True', 'to': u"orm['events.CustomRegFormEntry']"}),
            'discount_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'groups': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_primary': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'mail_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'meal_option': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'memberid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'override': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'override_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'position_title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'pricing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.RegConfPricing']", 'null': 'True'}),
            'registration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Registration']"}),
            'reminder': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'use_free_pass': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'events.registration': {
            'Meta': {'object_name': 'Registration'},
            'addons_added': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'amount_paid': ('django.db.models.fields.DecimalField', [], {'max_digits': '21', 'decimal_places': '2'}),
            'canceled': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_registrations'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Event']"}),
            'guid': ('django.db.models.fields.TextField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['invoices.Invoice']", 'null': 'True', 'blank': 'True'}),
            'is_table': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'override_price_table': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2', 'blank': 'True'}),
            'override_table': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_registrations'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payments.PaymentMethod']", 'null': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'reg_conf_price': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.RegConfPricing']", 'null': 'True'}),
            'reminder': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.registrationconfiguration': {
            'Meta': {'object_name': 'RegistrationConfiguration'},
            'allow_free_pass': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'bind_reg_form_to_conf_only': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'discount_eligible': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'display_registration_stats': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['emails.Email']", 'null': 'True'}),
            'enabled': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_guest_price': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'limit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'payment_method': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['payments.PaymentMethod']", 'symmetrical': 'False'}),
            'payment_required': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'reg_form': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'regconfs'", 'null': 'True', 'to': u"orm['events.CustomRegForm']"}),
            'registration_email_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'registration_email_type': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '20'}),
            'reminder_days': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'require_guests_info': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'send_reminder': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'use_custom_reg_form': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'})
        },
        u'events.speaker': {
            'Meta': {'object_name': 'Speaker'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'event': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['events.Event']", 'symmetrical': 'False', 'blank': 'True'}),
            'featured': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'events.sponsor': {
            'Meta': {'object_name': 'Sponsor'},
            'event': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['events.Event']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'events.standardregform': {
            'Meta': {'object_name': 'StandardRegForm', 'managed': 'False'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'events.type': {
            'Meta': {'object_name': 'Type'},
            'color_set': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.TypeColorSet']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'events.typecolorset': {
            'Meta': {'object_name': 'TypeColorSet'},
            'bg_color': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'border_color': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'fg_color': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'files.file': {
            'Meta': {'object_name': 'File'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'files_file_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'files_file_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '260'}),
            'file_cat': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'file_cat'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['files.FilesCategory']"}),
            'file_sub_cat': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'file_subcat'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['files.FilesCategory']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['user_groups.Group']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'files_file_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'tags': ('tagging.fields.TagField', [], {'null': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'files.filescategory': {
            'Meta': {'ordering': "('name',)", 'object_name': 'FilesCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['files.FilesCategory']", 'null': 'True'})
        },
        u'invoices.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'admin_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'arrival_date_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'bill_to': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'bill_to_address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'bill_to_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bill_to_company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bill_to_country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bill_to_email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bill_to_fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bill_to_first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bill_to_last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bill_to_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bill_to_state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bill_to_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'box_and_packing': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoice_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'disclaimer': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'discount_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'discount_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'fob': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'gift': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'greeting': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'is_void': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'object_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'other': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoice_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'payments_credits': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'po': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'project': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'receipt': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'ship_date': ('django.db.models.fields.DateTimeField', [], {}),
            'ship_to': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ship_to_address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'ship_to_address_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'ship_to_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'ship_to_country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'ship_to_fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'ship_to_first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'ship_to_state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'ship_via': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'shipping': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'shipping_surcharge': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'estimate'", 'max_length': '50'}),
            'subtotal': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '4'}),
            'tax_exempt': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'tax_exemptid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'tender_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'terms': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'total': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'variance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '4'}),
            'variance_notes': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'})
        },
        u'meta.meta': {
            'Meta': {'object_name': 'Meta'},
            'canonical_url': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'payments.paymentmethod': {
            'Meta': {'object_name': 'PaymentMethod'},
            'admin_only': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'human_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_online': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'user_groups.group': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Group'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_self_add': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'allow_self_remove': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'auto_respond': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'auto_respond_priority': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'user_groups_group_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'dashboard_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_recipient': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'user_groups_group_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'group': ('django.db.models.fields.related.OneToOneField', [], {'default': 'None', 'to': u"orm['auth.Group']", 'unique': 'True', 'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'through': u"orm['user_groups.GroupMembership']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'user_groups_group_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'group_permissions'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'show_as_option': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'slug': ('tendenci.apps.base.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'sync_newsletters': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'distribution'", 'max_length': '75', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'user_groups.groupmembership': {
            'Meta': {'unique_together': "(('group', 'member'),)", 'object_name': 'GroupMembership'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_groups.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_member'", 'to': u"orm['auth.User']"}),
            'owner_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['events']