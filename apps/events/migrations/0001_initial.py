# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'TypeColorSet'
        db.create_table('events_typecolorset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fg_color', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('bg_color', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('border_color', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('events', ['TypeColorSet'])

        # Adding model 'Type'
        db.create_table('events_type', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('color_set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.TypeColorSet'])),
        ))
        db.send_create_signal('events', ['Type'])

        # Adding model 'Place'
        db.create_table('events_place', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('events', ['Place'])

        # Adding model 'Registrant'
        db.create_table('events_registrant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('registration', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Registration'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mail_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('groups', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('position_title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('cancel_dt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('events', ['Registrant'])

        # Adding model 'Registration'
        db.create_table('events_registration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.TextField')(max_length=40)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
            ('reminder', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['invoices.Invoice'], null=True, blank=True)),
            ('payment_method', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.PaymentMethod'], null=True)),
            ('amount_paid', self.gf('django.db.models.fields.DecimalField')(max_digits=21, decimal_places=2)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_registrations', null=True, to=orm['auth.User'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_registrations', null=True, to=orm['auth.User'])),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('events', ['Registration'])

        # Adding model 'RegistrationConfiguration'
        db.create_table('events_registrationconfiguration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('early_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=21, decimal_places=2)),
            ('regular_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=21, decimal_places=2)),
            ('late_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=21, decimal_places=2)),
            ('early_dt', self.gf('django.db.models.fields.DateTimeField')()),
            ('regular_dt', self.gf('django.db.models.fields.DateTimeField')()),
            ('late_dt', self.gf('django.db.models.fields.DateTimeField')()),
            ('limit', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('events', ['RegistrationConfiguration'])

        # Adding M2M table for field payment_method on 'RegistrationConfiguration'
        db.create_table('events_registrationconfiguration_payment_method', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('registrationconfiguration', models.ForeignKey(orm['events.registrationconfiguration'], null=False)),
            ('paymentmethod', models.ForeignKey(orm['events.paymentmethod'], null=False))
        ))
        db.create_unique('events_registrationconfiguration_payment_method', ['registrationconfiguration_id', 'paymentmethod_id'])

        # Adding model 'Payment'
        db.create_table('events_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('registration', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['events.Registration'], unique=True)),
        ))
        db.send_create_signal('events', ['Payment'])

        # Adding model 'PaymentMethod'
        db.create_table('events_paymentmethod', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('events', ['PaymentMethod'])

        # Adding model 'Sponsor'
        db.create_table('events_sponsor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('events', ['Sponsor'])

        # Adding M2M table for field event on 'Sponsor'
        db.create_table('events_sponsor_event', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sponsor', models.ForeignKey(orm['events.sponsor'], null=False)),
            ('event', models.ForeignKey(orm['events.event'], null=False))
        ))
        db.create_unique('events_sponsor_event', ['sponsor_id', 'event_id'])

        # Adding model 'Discount'
        db.create_table('events_discount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('events', ['Discount'])

        # Adding model 'Organizer'
        db.create_table('events_organizer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('events', ['Organizer'])

        # Adding M2M table for field event on 'Organizer'
        db.create_table('events_organizer_event', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('organizer', models.ForeignKey(orm['events.organizer'], null=False)),
            ('event', models.ForeignKey(orm['events.event'], null=False))
        ))
        db.create_unique('events_organizer_event', ['organizer_id', 'event_id'])

        # Adding model 'Speaker'
        db.create_table('events_speaker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('events', ['Speaker'])

        # Adding M2M table for field event on 'Speaker'
        db.create_table('events_speaker_event', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('speaker', models.ForeignKey(orm['events.speaker'], null=False)),
            ('event', models.ForeignKey(orm['events.event'], null=False))
        ))
        db.create_unique('events_speaker_event', ['speaker_id', 'event_id'])

        # Adding model 'Event'
        db.create_table('events_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_user_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_anonymous_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_user_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='event_creator', to=orm['auth.User'])),
            ('creator_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='event_owner', to=orm['auth.User'])),
            ('owner_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('status_detail', self.gf('django.db.models.fields.CharField')(default='active', max_length=50)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entities.Entity'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Type'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('all_day', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('start_dt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 1, 24, 15, 2, 12, 220822))),
            ('end_dt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 1, 24, 15, 2, 12, 220859))),
            ('timezone', self.gf('timezones.fields.TimeZoneField')(default='US/Central', max_length=100)),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Place'], null=True)),
            ('registration_configuration', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['events.RegistrationConfiguration'], unique=True, null=True)),
            ('private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('meta', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['meta.Meta'], unique=True, null=True)),
        ))
        db.send_create_signal('events', ['Event'])


    def backwards(self, orm):
        
        # Deleting model 'TypeColorSet'
        db.delete_table('events_typecolorset')

        # Deleting model 'Type'
        db.delete_table('events_type')

        # Deleting model 'Place'
        db.delete_table('events_place')

        # Deleting model 'Registrant'
        db.delete_table('events_registrant')

        # Deleting model 'Registration'
        db.delete_table('events_registration')

        # Deleting model 'RegistrationConfiguration'
        db.delete_table('events_registrationconfiguration')

        # Removing M2M table for field payment_method on 'RegistrationConfiguration'
        db.delete_table('events_registrationconfiguration_payment_method')

        # Deleting model 'Payment'
        db.delete_table('events_payment')

        # Deleting model 'PaymentMethod'
        db.delete_table('events_paymentmethod')

        # Deleting model 'Sponsor'
        db.delete_table('events_sponsor')

        # Removing M2M table for field event on 'Sponsor'
        db.delete_table('events_sponsor_event')

        # Deleting model 'Discount'
        db.delete_table('events_discount')

        # Deleting model 'Organizer'
        db.delete_table('events_organizer')

        # Removing M2M table for field event on 'Organizer'
        db.delete_table('events_organizer_event')

        # Deleting model 'Speaker'
        db.delete_table('events_speaker')

        # Removing M2M table for field event on 'Speaker'
        db.delete_table('events_speaker_event')

        # Deleting model 'Event'
        db.delete_table('events_event')


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
        'entities.entity': {
            'Meta': {'object_name': 'Entity'},
            'admin_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'entity_parent_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'entity_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'})
        },
        'events.discount': {
            'Meta': {'object_name': 'Discount'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'events.event': {
            'Meta': {'object_name': 'Event'},
            'all_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'event_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 1, 24, 15, 2, 12, 220859)'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entities.Entity']", 'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['meta.Meta']", 'unique': 'True', 'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'event_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Place']", 'null': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'registration_configuration': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['events.RegistrationConfiguration']", 'unique': 'True', 'null': 'True'}),
            'start_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 1, 24, 15, 2, 12, 220822)'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'timezone': ('timezones.fields.TimeZoneField', [], {'default': "'US/Central'", 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Type']", 'null': 'True', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'events.organizer': {
            'Meta': {'object_name': 'Organizer'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'event': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['events.Event']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'events.payment': {
            'Meta': {'object_name': 'Payment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['events.Registration']", 'unique': 'True'})
        },
        'events.paymentmethod': {
            'Meta': {'object_name': 'PaymentMethod'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'events.place': {
            'Meta': {'object_name': 'Place'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'})
        },
        'events.registrant': {
            'Meta': {'object_name': 'Registrant'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'cancel_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'groups': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'position_title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'registration': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Registration']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'events.registration': {
            'Meta': {'object_name': 'Registration'},
            'amount_paid': ('django.db.models.fields.DecimalField', [], {'max_digits': '21', 'decimal_places': '2'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_registrations'", 'null': 'True', 'to': "orm['auth.User']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Event']"}),
            'guid': ('django.db.models.fields.TextField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoices.Invoice']", 'null': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_registrations'", 'null': 'True', 'to': "orm['auth.User']"}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.PaymentMethod']", 'null': 'True'}),
            'reminder': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'events.registrationconfiguration': {
            'Meta': {'object_name': 'RegistrationConfiguration'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'early_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'early_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'late_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'late_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2'}),
            'limit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'payment_method': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['events.PaymentMethod']", 'symmetrical': 'False'}),
            'regular_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'regular_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'events.speaker': {
            'Meta': {'object_name': 'Speaker'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'event': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['events.Event']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'events.sponsor': {
            'Meta': {'object_name': 'Sponsor'},
            'event': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['events.Event']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'events.type': {
            'Meta': {'object_name': 'Type'},
            'color_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.TypeColorSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'events.typecolorset': {
            'Meta': {'object_name': 'TypeColorSet'},
            'bg_color': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'border_color': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'fg_color': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'invoices.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'admin_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'arrival_date_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'bill_to': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'bill_to_address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bill_to_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bill_to_company': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
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
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoice_creator'", 'null': 'True', 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'disclaimer': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {}),
            'estimate': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'fob': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'gift': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'greeting': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'object_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'other': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoice_owner'", 'null': 'True', 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'payments_credits': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'po': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'project': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'receipt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ship_date': ('django.db.models.fields.DateTimeField', [], {}),
            'ship_to': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ship_to_address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'ship_to_address_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'ship_to_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_company': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
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
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'estimate'", 'max_length': '50'}),
            'subtotal': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '4'}),
            'tax_exempt': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tax_exemptid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tender_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'terms': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'total': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'variance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '4'}),
            'variance_notes': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'})
        },
        'meta.meta': {
            'Meta': {'object_name': 'Meta'},
            'canonical_url': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['events']
