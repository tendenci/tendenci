# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testimonials', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='testimonial',
            options={'ordering': ['position'], 'verbose_name': 'Testimonial', 'verbose_name_plural': 'Testimonials'},
        ),
        migrations.AddField(
            model_name='testimonial',
            name='position',
            field=models.IntegerField(default=0, null=True, verbose_name='Position', blank=True),
        ),
    ]
