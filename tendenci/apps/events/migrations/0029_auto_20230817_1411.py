# Generated by Django 3.2.18 on 2023-08-17 14:11

from django.db import migrations, models
import django.db.models.deletion
import tendenci.apps.events.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0028_auto_20230817_1154'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Additional image to display on certificate', upload_to='photos/certificates', verbose_name='Image')),
                ('name', models.CharField(help_text='Enter name to easily identify image', max_length=255, verbose_name='Name')),
            ],
            bases=(tendenci.apps.events.models.ImageMixin, models.Model),
        ),
        migrations.AddField(
            model_name='event',
            name='certificate_image',
            field=models.ForeignKey(blank=True, help_text='Optional photo to display on certificate.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='events.certificateimage'),
        ),
    ]
