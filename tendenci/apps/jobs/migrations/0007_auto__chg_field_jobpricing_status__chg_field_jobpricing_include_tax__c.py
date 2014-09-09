# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'JobPricing.status'
        db.alter_column(u'jobs_jobpricing', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'JobPricing.include_tax'
        db.alter_column(u'jobs_jobpricing', 'include_tax', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'JobPricing.show_member_pricing'
        db.alter_column(u'jobs_jobpricing', 'show_member_pricing', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Job.allow_user_view'
        db.alter_column(u'jobs_job', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Job.status'
        db.alter_column(u'jobs_job', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Job.syndicate'
        db.alter_column(u'jobs_job', 'syndicate', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Job.is_agency'
        db.alter_column(u'jobs_job', 'is_agency', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Job.allow_user_edit'
        db.alter_column(u'jobs_job', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Job.allow_member_view'
        db.alter_column(u'jobs_job', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Job.allow_member_edit'
        db.alter_column(u'jobs_job', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Job.allow_anonymous_view'
        db.alter_column(u'jobs_job', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'JobPricing.status'
        db.alter_column(u'jobs_jobpricing', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'JobPricing.include_tax'
        db.alter_column(u'jobs_jobpricing', 'include_tax', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'JobPricing.show_member_pricing'
        db.alter_column(u'jobs_jobpricing', 'show_member_pricing', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Job.allow_user_view'
        db.alter_column(u'jobs_job', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Job.status'
        db.alter_column(u'jobs_job', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Job.syndicate'
        db.alter_column(u'jobs_job', 'syndicate', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Job.is_agency'
        db.alter_column(u'jobs_job', 'is_agency', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Job.allow_user_edit'
        db.alter_column(u'jobs_job', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Job.allow_member_view'
        db.alter_column(u'jobs_job', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Job.allow_member_edit'
        db.alter_column(u'jobs_job', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Job.allow_anonymous_view'
        db.alter_column(u'jobs_job', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

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
        u'jobs.job': {
            'Meta': {'object_name': 'Job'},
            'activation_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'computer_skills': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contact_address': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'contact_address2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'contact_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'contact_company': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'contact_country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'contact_email': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'contact_fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'contact_method': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'contact_state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'contact_website': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'contact_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'jobs_job_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('tinymce.models.HTMLField', [], {}),
            'design_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'education': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'jobs_job_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'experience': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expiration_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['user_groups.Group']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['invoices.Invoice']", 'null': 'True', 'blank': 'True'}),
            'is_agency': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'job_url': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'list_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'member_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'member_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'meta': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['meta.Meta']", 'unique': 'True', 'null': 'True'}),
            'non_member_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'non_member_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'jobs_job_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'position_reports_to': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'post_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'pricing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jobs.JobPricing']", 'null': 'True'}),
            'requested_duration': ('django.db.models.fields.IntegerField', [], {}),
            'salary_from': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'salary_to': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'skills': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'slug': ('tendenci.apps.base.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'start_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'syndicate': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'jobs.jobpricing': {
            'Meta': {'object_name': 'JobPricing'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'job_pricing_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_tax': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'job_pricing_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'premium_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'premium_price_member': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'regular_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'regular_price_member': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'show_member_pricing': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '4', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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

    complete_apps = ['jobs']