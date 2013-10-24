# -*- coding: utf-8 -*-
from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        import os
        import uuid
        import shutil
        from django.conf import settings
        from tendenci.core.files.models import File
        from tendenci.core.newsletters.models import NewsletterTemplate

        newsletter_template = NewsletterTemplate.objects.create(
            template_id='pre-built-%s' % uuid.uuid1().get_hex()[:4],
            name=u'Pre-built Template')

        src_base_path = '%s/newsletters/templates/default/' % settings.STATIC_ROOT
        dst = '%s/files/newsletters/%s/' % (settings.MEDIA_ROOT, newsletter_template.template_id)

        if not os.path.exists(dst):
            os.makedirs(dst)

        # if src_base_path is not a directory, stop here
        if not os.path.isdir(src_base_path):
            return

        # move files
        for item in os.listdir(src_base_path):
            src = '%s%s' % (src_base_path, item)
            
            if os.path.isdir(dst):
                continue  # on to the next one

            shutil.copy2(src, dst)

            # create file record
            f = File.objects.create(
                name=item,
                file='files/newsletters/%s/%s' % (newsletter_template.template_id, item),
                description='Prebuilt template',
                content_type=NewsletterTemplate.get_content_type(),
                object_id=newsletter_template.pk,
                entity_id=1)

            if '.zip' in item:
                newsletter_template.zip_file = f.file.path
            elif '.html' in item:
                newsletter_template.html_file = f.file.path

        newsletter_template.save()


    def backwards(self, orm):
        "Write your backwards methods here."

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
    symmetrical = True
