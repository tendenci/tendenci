# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Metric.invoices'
        db.add_column('metrics_metric', 'invoices',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Metric.positive_invoices'
        db.add_column('metrics_metric', 'positive_invoices',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Metric.invoice_totals'
        db.add_column('metrics_metric', 'invoice_totals',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Metric.invoices'
        db.delete_column('metrics_metric', 'invoices')

        # Deleting field 'Metric.positive_invoices'
        db.delete_column('metrics_metric', 'positive_invoices')

        # Deleting field 'Metric.invoice_totals'
        db.delete_column('metrics_metric', 'invoice_totals')


    models = {
        'metrics.metric': {
            'Meta': {'object_name': 'Metric'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'disk_usage': ('django.db.models.fields.BigIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_totals': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2'}),
            'invoices': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'members': ('django.db.models.fields.IntegerField', [], {}),
            'positive_invoices': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'users': ('django.db.models.fields.IntegerField', [], {}),
            'visits': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['metrics']