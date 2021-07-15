# Generated by Django 2.2.24 on 2021-06-17 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0004_auto_20200902_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='show_for_donation',
            field=models.BooleanField(default=False, help_text='If checked, it will appear as an option for donation allocation on the donation form.', verbose_name='Use for Donation Allocation'),
        ),
    ]