# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ('invoices', '0007_populate_owner_field'),
        ('event_logs', '0003_base_to_homepage'),
    )

    def forwards(self, orm):
        "Write your forwards methods here."
        from django.core.management import call_command
        call_command("backfill_invoice_metrics")

    def backwards(self, orm):
        "Write your backwards methods here."
        pass

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
    symmetrical = True
