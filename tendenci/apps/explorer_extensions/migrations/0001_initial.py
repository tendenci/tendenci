# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DatabaseDumpFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_dt', models.DateTimeField(auto_now_add=True)),
                ('end_dt', models.DateTimeField(null=True, blank=True)),
                ('dbfile', models.FileField(upload_to='dbdump')),
                ('status', models.CharField(default='pending', max_length=50, choices=[('completed', 'Completed'), ('pending', 'Pending'), ('failed', 'Failed'), ('expired', 'Expired')])),
                ('export_format', models.CharField(default='json', max_length=20, choices=[('json', 'json'), ('xml', 'xml')])),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
    ]
