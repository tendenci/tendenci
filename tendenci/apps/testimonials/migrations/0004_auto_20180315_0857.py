# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testimonials', '0003_auto_20171023_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testimonial',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to='testimonials.TestimonialPhoto', help_text='Photo for this testimonial.', null=True),
        ),
    ]
