# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ArchitectureProject'
        db.create_table('architecture_projects_architectureproject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('allow_user_view', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('allow_member_view', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('allow_anonymous_edit', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('allow_user_edit', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('allow_member_edit', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='architectureproject_creator', to=orm['auth.User'])),
            ('creator_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='architectureproject_owner', to=orm['auth.User'])),
            ('owner_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('status_detail', self.gf('django.db.models.fields.CharField')(default='active', max_length=50)),
            ('client', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=150)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('overview', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('execution', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('results', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('tags', self.gf('tagging.fields.TagField')()),
        ))
        db.send_create_signal('architecture_projects', ['ArchitectureProject'])

        # Adding M2M table for field categories on 'ArchitectureProject'
        db.create_table('architecture_projects_architectureproject_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('architectureproject', models.ForeignKey(orm['architecture_projects.architectureproject'], null=False)),
            ('category', models.ForeignKey(orm['architecture_projects.category'], null=False))
        ))
        db.create_unique('architecture_projects_architectureproject_categories', ['architectureproject_id', 'category_id'])

        # Adding M2M table for field building_types on 'ArchitectureProject'
        db.create_table('architecture_projects_architectureproject_building_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('architectureproject', models.ForeignKey(orm['architecture_projects.architectureproject'], null=False)),
            ('building_type', models.ForeignKey(orm['architecture_projects.building_type'], null=False))
        ))
        db.create_unique('architecture_projects_architectureproject_building_types', ['architectureproject_id', 'building_type_id'])

        # Adding model 'Category'
        db.create_table('architecture_projects_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('architecture_projects', ['Category'])

        # Adding model 'BuildingType'
        db.create_table('architecture_projects_building_type', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('architecture_projects', ['BuildingType'])

        # Adding model 'Image'
        db.create_table('architecture_projects_image', (
            ('file_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['files.File'], unique=True, primary_key=True)),
            ('architecture_project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['architecture_projects.ArchitectureProject'])),
            ('position', self.gf('django.db.models.fields.IntegerField')(blank=True)),
        ))
        db.send_create_signal('architecture_projects', ['Image'])


    def backwards(self, orm):
        
        # Deleting model 'ArchitectureProject'
        db.delete_table('architecture_projects_architectureproject')

        # Removing M2M table for field categories on 'ArchitectureProject'
        db.delete_table('architecture_projects_architectureproject_categories')

        # Removing M2M table for field building_types on 'ArchitectureProject'
        db.delete_table('architecture_projects_architectureproject_building_types')

        # Deleting model 'Category'
        db.delete_table('architecture_projects_category')

        # Deleting model 'BuildingType'
        db.delete_table('architecture_projects_building_type')

        # Deleting model 'Image'
        db.delete_table('architecture_projects_image')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'architecture_projects.architectureproject': {
            'Meta': {'object_name': 'ArchitectureProject'},
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'client': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'architectureproject_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'execution': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overview': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'architectureproject_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'results': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['architecture_projects.Category']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'building_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['architecture_projects.BuildingType']", 'symmetrical': 'False'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '150'})
        },
        'architecture_projects.image': {
            'Meta': {'object_name': 'Image', '_ormbases': ['files.File']},
            'architecture_project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['architecture_projects.ArchitectureProject']"}),
            'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['files.File']", 'unique': 'True', 'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'blank': 'True'})
        },
        'architecture_projects.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'architecture_projects.building_type': {
            'Meta': {'object_name': 'BuildingType'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'files.file': {
            'Meta': {'object_name': 'File'},
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'file_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '260'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'file_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['architecture_projects']
