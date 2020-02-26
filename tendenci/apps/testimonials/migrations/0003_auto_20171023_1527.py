# -*- coding: utf-8 -*-


from django.db import migrations
# from tendenci.apps.testimonials.models import Testimonial


def assign_position(apps, schema_editor):
    Testimonial = apps.get_model("testimonials", "Testimonial")
    for i, t in enumerate(Testimonial.objects.all().order_by(('create_dt'))):
        t.position = i
        t.save()

class Migration(migrations.Migration):

    dependencies = [
        ('testimonials', '0002_auto_20171023_1502'),
    ]

    operations = [
        migrations.RunPython(assign_position),
    ]
