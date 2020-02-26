# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('label', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('data_type', models.CharField(max_length=10, choices=[('string', 'string'), ('boolean', 'boolean'), ('integer', 'int'), ('file', 'file'), ('decimal', 'decimal')])),
                ('value', models.TextField(blank=True)),
                ('default_value', models.TextField(blank=True)),
                ('input_type', models.CharField(max_length=25, choices=[('text', 'Text'), ('textarea', 'Textarea'), ('select', 'Select'), ('file', 'File')])),
                ('input_value', models.CharField(max_length=1000, blank=True)),
                ('client_editable', models.BooleanField(default=True)),
                ('store', models.BooleanField(default=True)),
                ('update_dt', models.DateTimeField(auto_now=True, null=True)),
                ('updated_by', models.CharField(max_length=50, blank=True)),
                ('scope', models.CharField(max_length=50)),
                ('scope_category', models.CharField(max_length=50)),
                ('parent_id', models.IntegerField(default=0, blank=True)),
                ('is_secure', models.BooleanField(default=False)),
            ],
        ),
    ]
