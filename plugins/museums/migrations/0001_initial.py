# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Museum'
        db.create_table('museums_museum', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_user_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_anonymous_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_user_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='museum_creator', to=orm['auth.User'])),
            ('creator_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='museum_owner', to=orm['auth.User'])),
            ('owner_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('status_detail', self.gf('django.db.models.fields.CharField')(default='active', max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('address', self.gf('django.db.models.fields.TextField')()),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('building_photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('about', self.gf('django.db.models.fields.TextField')()),
            ('hours', self.gf('django.db.models.fields.TextField')()),
            ('free_times', self.gf('django.db.models.fields.TextField')()),
            ('parking_information', self.gf('django.db.models.fields.TextField')()),
            ('free_parking', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('street_parking', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('paid_parking', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dining_information', self.gf('django.db.models.fields.TextField')()),
            ('restaurant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('snacks', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('shopping_information', self.gf('django.db.models.fields.TextField')()),
            ('events', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('special_offers', self.gf('django.db.models.fields.TextField')()),
            ('facebook', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('twitter', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('flickr', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('youtube', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('museums', ['Museum'])

        # Adding model 'Photo'
        db.create_table('museums_photo', (
            ('file_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['files.File'], unique=True, primary_key=True)),
            ('museum', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['museums.Museum'])),
        ))
        db.send_create_signal('museums', ['Photo'])


    def backwards(self, orm):
        
        # Deleting model 'Museum'
        db.delete_table('museums_museum')

        # Deleting model 'Photo'
        db.delete_table('museums_photo')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'files.file': {
            'Meta': {'object_name': 'File'},
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'file_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '260'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'file_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'museums.museum': {
            'Meta': {'object_name': 'Museum'},
            'about': ('django.db.models.fields.TextField', [], {}),
            'address': ('django.db.models.fields.TextField', [], {}),
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'building_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'museum_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'dining_information': ('django.db.models.fields.TextField', [], {}),
            'events': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'facebook': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'flickr': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'free_parking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'free_times': ('django.db.models.fields.TextField', [], {}),
            'hours': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'museum_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'paid_parking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parking_information': ('django.db.models.fields.TextField', [], {}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'restaurant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shopping_information': ('django.db.models.fields.TextField', [], {}),
            'snacks': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'special_offers': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'street_parking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'twitter': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'youtube': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'museums.photo': {
            'Meta': {'object_name': 'Photo', '_ormbases': ['files.File']},
            'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['files.File']", 'unique': 'True', 'primary_key': 'True'}),
            'museum': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['museums.Museum']"})
        }
    }

    complete_apps = ['museums']
