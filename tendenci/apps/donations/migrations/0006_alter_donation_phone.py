# Generated by Django 4.2.21 on 2025-06-15 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0005_auto_20240409_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
