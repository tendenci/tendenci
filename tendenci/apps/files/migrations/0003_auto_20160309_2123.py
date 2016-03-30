# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.db import migrations


def assign_file_type(apps, schema_editor):
    types = {
            'image': ('.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff', '.bmp'),
            'text': ('.txt', '.doc', '.docx'),
            'spreadsheet': ('.csv', '.xls', '.xlsx'),
            'powerpoint': ('.ppt', '.pptx'),
            'pdf': ('.pdf'),
            'video': ('.wmv', '.mov', '.mpg', '.mp4', '.m4v'),
            'zip': ('.zip'),
        }
    File = apps.get_model("files", "File")
    for f in File.objects.all():
        # we only need to update the f_type feild - don't use save()
        ext = os.path.splitext(f.file.name)[-1]
        f_type = ''
        for type in types:
            if ext in types[type]:
                f_type = type
                break

        if f_type:
            File.objects.filter(id=f.id).update(f_type=f_type)

class Migration(migrations.Migration):

    dependencies = [
        ('files', '0002_file_f_type'),
    ]

    operations = [
        migrations.RunPython(assign_file_type),
    ]
