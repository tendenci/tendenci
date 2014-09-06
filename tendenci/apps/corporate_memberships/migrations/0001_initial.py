# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CorporateMembershipType'
        db.create_table('corporate_memberships_corporatemembershiptype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_user_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_anonymous_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_user_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='corporate_memberships_corporatemembershiptype_creator', to=orm['auth.User'])),
            ('creator_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='corporate_memberships_corporatemembershiptype_owner', to=orm['auth.User'])),
            ('owner_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('status_detail', self.gf('django.db.models.fields.CharField')(default='active', max_length=50)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=15, decimal_places=2, blank=True)),
            ('renewal_price', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=15, decimal_places=2, blank=True)),
            ('membership_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memberships.MembershipType'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('admin_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('apply_threshold', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('individual_threshold', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('individual_threshold_price', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=15, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('corporate_memberships', ['CorporateMembershipType'])

        # Adding model 'CorporateMembership'
        db.create_table('corporate_memberships_corporatemembership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_user_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_anonymous_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_user_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='corporate_memberships_corporatemembership_creator', to=orm['auth.User'])),
            ('creator_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='corporate_memberships_corporatemembership_owner', to=orm['auth.User'])),
            ('owner_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('status_detail', self.gf('django.db.models.fields.CharField')(default='active', max_length=50)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('corporate_membership_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corporate_memberships.CorporateMembershipType'])),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('address2', self.gf('django.db.models.fields.CharField')(default='', max_length=100, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('secret_code', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('renewal', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('renew_entry_id', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('join_dt', self.gf('django.db.models.fields.DateTimeField')()),
            ('renew_dt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('expiration_dt', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('approved_denied_dt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('approved_denied_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('payment_method', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['payments.PaymentMethod'], null=True)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['invoices.Invoice'], null=True, blank=True)),
            ('anonymous_creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corporate_memberships.Creator'], null=True)),
            ('corp_app', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corporate_memberships.CorpApp'])),
        ))
        db.send_create_signal('corporate_memberships', ['CorporateMembership'])

        # Adding model 'Creator'
        db.create_table('corporate_memberships_creator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('hash', self.gf('django.db.models.fields.CharField')(default='', max_length=32)),
        ))
        db.send_create_signal('corporate_memberships', ['Creator'])

        # Adding model 'AuthorizedDomain'
        db.create_table('corporate_memberships_authorizeddomain', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corporate_membership', self.gf('django.db.models.fields.related.ForeignKey')(related_name='auth_domains', to=orm['corporate_memberships.CorporateMembership'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('corporate_memberships', ['AuthorizedDomain'])

        # Adding model 'CorporateMembershipRep'
        db.create_table('corporate_memberships_corporatemembershiprep', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corporate_membership', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reps', to=orm['corporate_memberships.CorporateMembership'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_dues_rep', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_member_rep', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('corporate_memberships', ['CorporateMembershipRep'])

        # Adding unique constraint on 'CorporateMembershipRep', fields ['corporate_membership', 'user']
        db.create_unique('corporate_memberships_corporatemembershiprep', ['corporate_membership_id', 'user_id'])

        # Adding model 'CorporateMembershipArchive'
        db.create_table('corporate_memberships_corporatemembershiparchive', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_user_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_anonymous_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_user_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='corporate_memberships_corporatemembershiparchive_creator', to=orm['auth.User'])),
            ('creator_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='corporate_memberships_corporatemembershiparchive_owner', to=orm['auth.User'])),
            ('owner_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('status_detail', self.gf('django.db.models.fields.CharField')(default='active', max_length=50)),
            ('corporate_membership', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corporate_memberships.CorporateMembership'])),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('corporate_membership_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corporate_memberships.CorporateMembershipType'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('address2', self.gf('django.db.models.fields.CharField')(default='', max_length=100, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('secret_code', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('renewal', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('renew_entry_id', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['invoices.Invoice'], null=True, blank=True)),
            ('join_dt', self.gf('django.db.models.fields.DateTimeField')()),
            ('renew_dt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('expiration_dt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('approved_denied_dt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('approved_denied_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('payment_method', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['payments.PaymentMethod'], null=True)),
            ('corp_memb_create_dt', self.gf('django.db.models.fields.DateTimeField')()),
            ('corp_memb_update_dt', self.gf('django.db.models.fields.DateTimeField')()),
            ('archive_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='corp_memb_archiver', null=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('corporate_memberships', ['CorporateMembershipArchive'])

        # Adding model 'CorpMembRenewEntry'
        db.create_table('corporate_memberships_corpmembrenewentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corporate_membership', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corporate_memberships.CorporateMembership'])),
            ('corporate_membership_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corporate_memberships.CorporateMembershipType'])),
            ('payment_method', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['invoices.Invoice'], null=True, blank=True)),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('status_detail', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('corporate_memberships', ['CorpMembRenewEntry'])

        # Adding model 'IndivMembRenewEntry'
        db.create_table('corporate_memberships_indivmembrenewentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corp_memb_renew_entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corporate_memberships.CorpMembRenewEntry'])),
            ('membership', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memberships.Membership'])),
        ))
        db.send_create_signal('corporate_memberships', ['IndivMembRenewEntry'])

        # Adding model 'IndivMembEmailVeri8n'
        db.create_table('corporate_memberships_indivmembemailveri8n', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('corporate_membership', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corporate_memberships.CorporateMembership'])),
            ('verified_email', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('verified_dt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ime_veri8n_creator', null=True, to=orm['auth.User'])),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ime_veri8n_updator', null=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('corporate_memberships', ['IndivMembEmailVeri8n'])

        # Adding model 'CorpFieldEntry'
        db.create_table('corporate_memberships_corpfieldentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corporate_membership', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['corporate_memberships.CorporateMembership'])),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='field', to=orm['corporate_memberships.CorpField'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=2000)),
        ))
        db.send_create_signal('corporate_memberships', ['CorpFieldEntry'])

        # Adding model 'CorpApp'
        db.create_table('corporate_memberships_corpapp', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_user_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_anonymous_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_user_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='corporate_memberships_corpapp_creator', to=orm['auth.User'])),
            ('creator_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='corporate_memberships_corpapp_owner', to=orm['auth.User'])),
            ('owner_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('status_detail', self.gf('django.db.models.fields.CharField')(default='active', max_length=50)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=155)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=155, db_index=True)),
            ('authentication_method', self.gf('django.db.models.fields.CharField')(default='admin', max_length=50)),
            ('description', self.gf('tinymce.models.HTMLField')(null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('confirmation_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('memb_app', self.gf('django.db.models.fields.related.OneToOneField')(related_name='corp_app', unique=True, to=orm['memberships.App'])),
        ))
        db.send_create_signal('corporate_memberships', ['CorpApp'])

        # Adding M2M table for field corp_memb_type on 'CorpApp'
        db.create_table('corporate_memberships_corpapp_corp_memb_type', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('corpapp', models.ForeignKey(orm['corporate_memberships.corpapp'], null=False)),
            ('corporatemembershiptype', models.ForeignKey(orm['corporate_memberships.corporatemembershiptype'], null=False))
        ))
        db.create_unique('corporate_memberships_corpapp_corp_memb_type', ['corpapp_id', 'corporatemembershiptype_id'])

        # Adding M2M table for field payment_methods on 'CorpApp'
        db.create_table('corporate_memberships_corpapp_payment_methods', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('corpapp', models.ForeignKey(orm['corporate_memberships.corpapp'], null=False)),
            ('paymentmethod', models.ForeignKey(orm['payments.paymentmethod'], null=False))
        ))
        db.create_unique('corporate_memberships_corpapp_payment_methods', ['corpapp_id', 'paymentmethod_id'])

        # Adding model 'CorpField'
        db.create_table('corporate_memberships_corpfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corp_app', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['corporate_memberships.CorpApp'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('field_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('object_type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('field_type', self.gf('django.db.models.fields.CharField')(default='CharField', max_length=80, null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('choices', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('field_layout', self.gf('django.db.models.fields.CharField')(default='1', max_length=50, null=True, blank=True)),
            ('size', self.gf('django.db.models.fields.CharField')(default='m', max_length=1, null=True, blank=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('no_duplicates', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('admin_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('instruction', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True, blank=True)),
            ('default_value', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('css_class', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('corporate_memberships', ['CorpField'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'CorporateMembershipRep', fields ['corporate_membership', 'user']
        db.delete_unique('corporate_memberships_corporatemembershiprep', ['corporate_membership_id', 'user_id'])

        # Deleting model 'CorporateMembershipType'
        db.delete_table('corporate_memberships_corporatemembershiptype')

        # Deleting model 'CorporateMembership'
        db.delete_table('corporate_memberships_corporatemembership')

        # Deleting model 'Creator'
        db.delete_table('corporate_memberships_creator')

        # Deleting model 'AuthorizedDomain'
        db.delete_table('corporate_memberships_authorizeddomain')

        # Deleting model 'CorporateMembershipRep'
        db.delete_table('corporate_memberships_corporatemembershiprep')

        # Deleting model 'CorporateMembershipArchive'
        db.delete_table('corporate_memberships_corporatemembershiparchive')

        # Deleting model 'CorpMembRenewEntry'
        db.delete_table('corporate_memberships_corpmembrenewentry')

        # Deleting model 'IndivMembRenewEntry'
        db.delete_table('corporate_memberships_indivmembrenewentry')

        # Deleting model 'IndivMembEmailVeri8n'
        db.delete_table('corporate_memberships_indivmembemailveri8n')

        # Deleting model 'CorpFieldEntry'
        db.delete_table('corporate_memberships_corpfieldentry')

        # Deleting model 'CorpApp'
        db.delete_table('corporate_memberships_corpapp')

        # Removing M2M table for field corp_memb_type on 'CorpApp'
        db.delete_table('corporate_memberships_corpapp_corp_memb_type')

        # Removing M2M table for field payment_methods on 'CorpApp'
        db.delete_table('corporate_memberships_corpapp_payment_methods')

        # Deleting model 'CorpField'
        db.delete_table('corporate_memberships_corpfield')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 19, 15, 24, 34, 663941)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 19, 15, 24, 34, 663775)'}),
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
        'corporate_memberships.authorizeddomain': {
            'Meta': {'object_name': 'AuthorizedDomain'},
            'corporate_membership': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'auth_domains'", 'to': "orm['corporate_memberships.CorporateMembership']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'corporate_memberships.corpapp': {
            'Meta': {'ordering': "('name',)", 'object_name': 'CorpApp'},
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'authentication_method': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '50'}),
            'confirmation_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'corp_memb_type': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['corporate_memberships.CorporateMembershipType']", 'symmetrical': 'False'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corporate_memberships_corpapp_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memb_app': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'corp_app'", 'unique': 'True', 'to': "orm['memberships.App']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '155'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corporate_memberships_corpapp_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_methods': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['payments.PaymentMethod']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '155', 'db_index': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'corporate_memberships.corpfield': {
            'Meta': {'ordering': "('order',)", 'object_name': 'CorpField'},
            'admin_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'choices': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'corp_app': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['corporate_memberships.CorpApp']"}),
            'css_class': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'default_value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'field_layout': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'default': "'CharField'", 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instruction': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'no_duplicates': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'size': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'corporate_memberships.corpfieldentry': {
            'Meta': {'object_name': 'CorpFieldEntry'},
            'corporate_membership': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['corporate_memberships.CorporateMembership']"}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'field'", 'to': "orm['corporate_memberships.CorpField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        },
        'corporate_memberships.corpmembrenewentry': {
            'Meta': {'object_name': 'CorpMembRenewEntry'},
            'corporate_membership': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corporate_memberships.CorporateMembership']"}),
            'corporate_membership_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corporate_memberships.CorporateMembershipType']"}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoices.Invoice']", 'null': 'True', 'blank': 'True'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'corporate_memberships.corporatemembership': {
            'Meta': {'object_name': 'CorporateMembership'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'anonymous_creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corporate_memberships.Creator']", 'null': 'True'}),
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'approved_denied_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'approved_denied_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'corp_app': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corporate_memberships.CorpApp']"}),
            'corporate_membership_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corporate_memberships.CorporateMembershipType']"}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corporate_memberships_corporatemembership_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'expiration_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoices.Invoice']", 'null': 'True', 'blank': 'True'}),
            'join_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corporate_memberships_corporatemembership_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['payments.PaymentMethod']", 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'renew_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'renew_entry_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'renewal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'secret_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'corporate_memberships.corporatemembershiparchive': {
            'Meta': {'object_name': 'CorporateMembershipArchive'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'approved_denied_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'approved_denied_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'archive_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corp_memb_archiver'", 'null': 'True', 'to': "orm['auth.User']"}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'corp_memb_create_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'corp_memb_update_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'corporate_membership': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corporate_memberships.CorporateMembership']"}),
            'corporate_membership_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corporate_memberships.CorporateMembershipType']"}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corporate_memberships_corporatemembershiparchive_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'expiration_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoices.Invoice']", 'null': 'True', 'blank': 'True'}),
            'join_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corporate_memberships_corporatemembershiparchive_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['payments.PaymentMethod']", 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'renew_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'renew_entry_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'renewal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'secret_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'corporate_memberships.corporatemembershiprep': {
            'Meta': {'unique_together': "(('corporate_membership', 'user'),)", 'object_name': 'CorporateMembershipRep'},
            'corporate_membership': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reps'", 'to': "orm['corporate_memberships.CorporateMembership']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_dues_rep': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_member_rep': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'corporate_memberships.corporatemembershiptype': {
            'Meta': {'object_name': 'CorporateMembershipType'},
            'admin_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'apply_threshold': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corporate_memberships_corporatemembershiptype_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individual_threshold': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'individual_threshold_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'membership_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memberships.MembershipType']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corporate_memberships_corporatemembershiptype_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'renewal_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'corporate_memberships.creator': {
            'Meta': {'object_name': 'Creator'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        'corporate_memberships.indivmembemailveri8n': {
            'Meta': {'object_name': 'IndivMembEmailVeri8n'},
            'corporate_membership': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corporate_memberships.CorporateMembership']"}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ime_veri8n_creator'", 'null': 'True', 'to': "orm['auth.User']"}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ime_veri8n_updator'", 'null': 'True', 'to': "orm['auth.User']"}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'verified_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'verified_email': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'corporate_memberships.indivmembrenewentry': {
            'Meta': {'object_name': 'IndivMembRenewEntry'},
            'corp_memb_renew_entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corporate_memberships.CorpMembRenewEntry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'membership': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memberships.Membership']"})
        },
        'entities.entity': {
            'Meta': {'object_name': 'Entity'},
            'admin_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
        'memberships.app': {
            'Meta': {'object_name': 'App'},
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'confirmation_text': ('tinymce.models.HTMLField', [], {}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships_app_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'membership_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['memberships.MembershipType']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '155'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships_app_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_methods': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['payments.PaymentMethod']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'use_captcha': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'use_for_corp': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'memberships.membership': {
            'Meta': {'object_name': 'Membership'},
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'corporate_membership_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships_membership_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'expire_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoices.Invoice']", 'null': 'True', 'blank': 'True'}),
            'ma': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memberships.App']", 'null': 'True'}),
            'member_number': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'membership_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memberships.MembershipType']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships_membership_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payments.PaymentMethod']", 'null': 'True', 'blank': 'True'}),
            'renewal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'send_notice': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'subscribe_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships'", 'to': "orm['auth.User']"})
        },
        'memberships.membershiptype': {
            'Meta': {'object_name': 'MembershipType'},
            'admin_fee': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'admin_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_renewal': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships_membershiptype_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'expiration_grace_period': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fixed_option': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'fixed_option1_day': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fixed_option1_month': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fixed_option1_year': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fixed_option2_can_rollover': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fixed_option2_day': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fixed_option2_month': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fixed_option2_rollover_days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'membership_types'", 'to': "orm['user_groups.Group']"}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'never_expires': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships_membershiptype_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'period': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'period_type': ('django.db.models.fields.CharField', [], {'default': "'rolling'", 'max_length': '10'}),
            'period_unit': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'renewal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'renewal_period_end': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'renewal_period_start': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'renewal_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'renewal_require_approval': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'require_approval': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'rolling_option': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rolling_option1_day': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rolling_renew_option': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rolling_renew_option1_day': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rolling_renew_option2_day': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'payments.paymentmethod': {
            'Meta': {'object_name': 'PaymentMethod'},
            'admin_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'human_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_online': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
        'user_groups.group': {
            'Meta': {'object_name': 'Group'},
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_self_add': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_self_remove': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_respond': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_respond_priority': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'auto_respond_template': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_groups_group_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_recipient': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entities.Entity']", 'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "orm['user_groups.GroupMembership']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_groups_group_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'group_permissions'", 'blank': 'True', 'to': "orm['auth.Permission']"}),
            'show_as_option': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('tendenci.core.base.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
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

    complete_apps = ['corporate_memberships']
