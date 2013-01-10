# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Profile.ud6'
        db.add_column('profiles_profile', 'ud6', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud7'
        db.add_column('profiles_profile', 'ud7', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud8'
        db.add_column('profiles_profile', 'ud8', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud9'
        db.add_column('profiles_profile', 'ud9', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud10'
        db.add_column('profiles_profile', 'ud10', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud11'
        db.add_column('profiles_profile', 'ud11', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud12'
        db.add_column('profiles_profile', 'ud12', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud13'
        db.add_column('profiles_profile', 'ud13', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud14'
        db.add_column('profiles_profile', 'ud14', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud15'
        db.add_column('profiles_profile', 'ud15', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud16'
        db.add_column('profiles_profile', 'ud16', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud17'
        db.add_column('profiles_profile', 'ud17', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud18'
        db.add_column('profiles_profile', 'ud18', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud19'
        db.add_column('profiles_profile', 'ud19', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud20'
        db.add_column('profiles_profile', 'ud20', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud21'
        db.add_column('profiles_profile', 'ud21', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud22'
        db.add_column('profiles_profile', 'ud22', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud23'
        db.add_column('profiles_profile', 'ud23', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud24'
        db.add_column('profiles_profile', 'ud24', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud25'
        db.add_column('profiles_profile', 'ud25', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud26'
        db.add_column('profiles_profile', 'ud26', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud27'
        db.add_column('profiles_profile', 'ud27', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud28'
        db.add_column('profiles_profile', 'ud28', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud29'
        db.add_column('profiles_profile', 'ud29', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)

        # Adding field 'Profile.ud30'
        db.add_column('profiles_profile', 'ud30', self.gf('django.db.models.fields.TextField')(default=u'', blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Profile.ud6'
        db.delete_column('profiles_profile', 'ud6')

        # Deleting field 'Profile.ud7'
        db.delete_column('profiles_profile', 'ud7')

        # Deleting field 'Profile.ud8'
        db.delete_column('profiles_profile', 'ud8')

        # Deleting field 'Profile.ud9'
        db.delete_column('profiles_profile', 'ud9')

        # Deleting field 'Profile.ud10'
        db.delete_column('profiles_profile', 'ud10')

        # Deleting field 'Profile.ud11'
        db.delete_column('profiles_profile', 'ud11')

        # Deleting field 'Profile.ud12'
        db.delete_column('profiles_profile', 'ud12')

        # Deleting field 'Profile.ud13'
        db.delete_column('profiles_profile', 'ud13')

        # Deleting field 'Profile.ud14'
        db.delete_column('profiles_profile', 'ud14')

        # Deleting field 'Profile.ud15'
        db.delete_column('profiles_profile', 'ud15')

        # Deleting field 'Profile.ud16'
        db.delete_column('profiles_profile', 'ud16')

        # Deleting field 'Profile.ud17'
        db.delete_column('profiles_profile', 'ud17')

        # Deleting field 'Profile.ud18'
        db.delete_column('profiles_profile', 'ud18')

        # Deleting field 'Profile.ud19'
        db.delete_column('profiles_profile', 'ud19')

        # Deleting field 'Profile.ud20'
        db.delete_column('profiles_profile', 'ud20')

        # Deleting field 'Profile.ud21'
        db.delete_column('profiles_profile', 'ud21')

        # Deleting field 'Profile.ud22'
        db.delete_column('profiles_profile', 'ud22')

        # Deleting field 'Profile.ud23'
        db.delete_column('profiles_profile', 'ud23')

        # Deleting field 'Profile.ud24'
        db.delete_column('profiles_profile', 'ud24')

        # Deleting field 'Profile.ud25'
        db.delete_column('profiles_profile', 'ud25')

        # Deleting field 'Profile.ud26'
        db.delete_column('profiles_profile', 'ud26')

        # Deleting field 'Profile.ud27'
        db.delete_column('profiles_profile', 'ud27')

        # Deleting field 'Profile.ud28'
        db.delete_column('profiles_profile', 'ud28')

        # Deleting field 'Profile.ud29'
        db.delete_column('profiles_profile', 'ud29')

        # Deleting field 'Profile.ud30'
        db.delete_column('profiles_profile', 'ud30')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 10, 13, 49, 38, 724864)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 10, 13, 49, 38, 724684)'}),
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
        'entities.entity': {
            'Meta': {'ordering': "('entity_name',)", 'object_name': 'Entity'},
            'admin_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_creator'", 'null': 'True', 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'entity_parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entity_children'", 'null': 'True', 'to': "orm['entities.Entity']"}),
            'entity_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_owner'", 'null': 'True', 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'})
        },
        'perms.objectpermission': {
            'Meta': {'object_name': 'ObjectPermission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_groups.Group']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'profiles.profile': {
            'Meta': {'object_name': 'Profile'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'address_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'admin_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'agreed_to_tos': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'profiles_profile_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'direct_mail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'dob': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'education': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'email2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entities.Entity']", 'null': 'True', 'blank': 'True'}),
            'exported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'first_responder': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'hide_address': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hide_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hide_in_search': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hide_phone': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'historical_member_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'home_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initials': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en-us'", 'max_length': '10'}),
            'mailing_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'member_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'mobile_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'original_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'profiles_profile_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'pl_id': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'position_assignment': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'position_title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'referral_source': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'remember_login': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'salutation': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'spouse': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'student': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time_zone': ('timezones.fields.TimeZoneField', [], {'default': "'America/Chicago'", 'max_length': '100'}),
            'ud1': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud10': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud11': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud12': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud13': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud14': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud15': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud16': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud17': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud18': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud19': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud2': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud20': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud21': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud22': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud23': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud24': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud25': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud26': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud27': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud28': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud29': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud3': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud30': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud4': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud5': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud6': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud7': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud8': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'ud9': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'url2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'work_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'user_groups.group': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Group'},
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_self_add': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_self_remove': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_respond': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_respond_priority': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'user_groups_group_creator'", 'null': 'True', 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_recipient': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'user_groups_group_entity'", 'null': 'True', 'blank': 'True', 'to': "orm['entities.Entity']"}),
            'group': ('django.db.models.fields.related.OneToOneField', [], {'default': 'None', 'to': "orm['auth.Group']", 'unique': 'True', 'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "orm['user_groups.GroupMembership']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'user_groups_group_owner'", 'null': 'True', 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'group_permissions'", 'blank': 'True', 'to': "orm['auth.Permission']"}),
            'show_as_option': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('tendenci.core.base.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'sync_newsletters': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'distribution'", 'max_length': '75', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'user_groups.groupmembership': {
            'Meta': {'unique_together': "(('group', 'member'),)", 'object_name': 'GroupMembership'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_groups.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_member'", 'to': "orm['auth.User']"}),
            'owner_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['profiles']
