# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'NewsletterTemplate'
        db.create_table('newsletters_newslettertemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template_id', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('html_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('zip_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
        ))
        db.send_create_signal('newsletters', ['NewsletterTemplate'])


    def backwards(self, orm):
        
        # Deleting model 'NewsletterTemplate'
        db.delete_table('newsletters_newslettertemplate')


    models = {
        'newsletters.newslettertemplate': {
            'Meta': {'object_name': 'NewsletterTemplate'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'html_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'template_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True', 'null': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'zip_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'})
        }
    }

    complete_apps = ['newsletters']
