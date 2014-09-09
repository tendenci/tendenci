# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'PaymentProfile.status'
        db.alter_column(u'recurring_payments_paymentprofile', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'PaymentProfile.creator'
        db.alter_column(u'recurring_payments_paymentprofile', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'PaymentProfile.owner'
        db.alter_column(u'recurring_payments_paymentprofile', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'RecurringPayment.owner'
        db.alter_column(u'recurring_payments_recurringpayment', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'RecurringPayment.creator'
        db.alter_column(u'recurring_payments_recurringpayment', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'RecurringPayment.status'
        db.alter_column(u'recurring_payments_recurringpayment', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RecurringPayment.tax_rate'
        db.alter_column(u'recurring_payments_recurringpayment', 'tax_rate', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=6))

        # Changing field 'RecurringPayment.user'
        db.alter_column(u'recurring_payments_recurringpayment', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'RecurringPayment.taxable'
        db.alter_column(u'recurring_payments_recurringpayment', 'taxable', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RecurringPayment.tax_exempt'
        db.alter_column(u'recurring_payments_recurringpayment', 'tax_exempt', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'RecurringPayment.has_trial_period'
        db.alter_column(u'recurring_payments_recurringpayment', 'has_trial_period', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'PaymentTransaction.status'
        db.alter_column(u'recurring_payments_paymenttransaction', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'PaymentTransaction.creator'
        db.alter_column(u'recurring_payments_paymenttransaction', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

    def backwards(self, orm):

        # Changing field 'PaymentProfile.status'
        db.alter_column(u'recurring_payments_paymentprofile', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'PaymentProfile.creator'
        db.alter_column(u'recurring_payments_paymentprofile', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'PaymentProfile.owner'
        db.alter_column(u'recurring_payments_paymentprofile', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'RecurringPayment.owner'
        db.alter_column(u'recurring_payments_recurringpayment', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'RecurringPayment.creator'
        db.alter_column(u'recurring_payments_recurringpayment', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'RecurringPayment.status'
        db.alter_column(u'recurring_payments_recurringpayment', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RecurringPayment.tax_rate'
        db.alter_column(u'recurring_payments_recurringpayment', 'tax_rate', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=4))

        # Changing field 'RecurringPayment.user'
        db.alter_column(u'recurring_payments_recurringpayment', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'RecurringPayment.taxable'
        db.alter_column(u'recurring_payments_recurringpayment', 'taxable', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RecurringPayment.tax_exempt'
        db.alter_column(u'recurring_payments_recurringpayment', 'tax_exempt', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RecurringPayment.has_trial_period'
        db.alter_column(u'recurring_payments_recurringpayment', 'has_trial_period', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'PaymentTransaction.status'
        db.alter_column(u'recurring_payments_paymenttransaction', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'PaymentTransaction.creator'
        db.alter_column(u'recurring_payments_paymenttransaction', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

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
        u'payments.payment': {
            'Meta': {'object_name': 'Payment'},
            'account_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4', 'null': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'auth_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'avs_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'card_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payment_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'cust_id': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1600'}),
            'duty': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'freight': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['invoices.Invoice']"}),
            'invoice_num': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'md5_hash': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payment_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'payment_attempted': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'payment_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'po_num': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'response_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2'}),
            'response_page': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'response_reason_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15'}),
            'response_reason_text': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'response_subcode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'}),
            'ship_to_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'null': 'True'}),
            'ship_to_city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'null': 'True'}),
            'ship_to_company': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True'}),
            'ship_to_country': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'null': 'True'}),
            'ship_to_first_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True'}),
            'ship_to_last_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True'}),
            'ship_to_state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'null': 'True'}),
            'ship_to_zip': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'submit_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'tax': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'tax_exempt': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'trans_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'trans_string': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'verified': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'recurring_payments.paymentprofile': {
            'Meta': {'object_name': 'PaymentProfile'},
            'card_num': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True'}),
            'card_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payment_profile_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'customer_profile_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'expiration_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payment_profile_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'payment_profile_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'recurring_payments.paymenttransaction': {
            'Meta': {'object_name': 'PaymentTransaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payment_transaction_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'message_text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payments.Payment']", 'null': 'True'}),
            'payment_profile_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'recurring_payment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['recurring_payments.RecurringPayment']"}),
            'recurring_payment_invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['recurring_payments.RecurringPaymentInvoice']"}),
            'result_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'trans_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        u'recurring_payments.recurringpayment': {
            'Meta': {'object_name': 'RecurringPayment'},
            'billing_frequency': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'billing_period': ('django.db.models.fields.CharField', [], {'default': "'month'", 'max_length': '50'}),
            'billing_start_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recurring_payment_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'current_balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'customer_profile_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'due_sore': ('django.db.models.fields.CharField', [], {'default': "'start'", 'max_length': '20'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'has_trial_period': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_payment_received_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'next_billing_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'num_billing_cycle_completed': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'num_billing_cycle_failed': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'num_days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'object_content_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'object_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'outstanding_balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recurring_payment_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'payment_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'tax_exempt': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '6', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'trial_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'trial_period_end_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'trial_period_start_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recurring_payment_user'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"})
        },
        u'recurring_payments.recurringpaymentinvoice': {
            'Meta': {'object_name': 'RecurringPaymentInvoice'},
            'billing_cycle_end_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'billing_cycle_start_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'billing_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['invoices.Invoice']", 'null': 'True', 'blank': 'True'}),
            'last_payment_failed_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'payment_received_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'recurring_payment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rp_invoices'", 'to': u"orm['recurring_payments.RecurringPayment']"})
        }
    }

    complete_apps = ['recurring_payments']