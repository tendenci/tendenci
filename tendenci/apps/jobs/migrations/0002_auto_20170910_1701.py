# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='jobs.Category', null=True, on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.AddField(
            model_name='job',
            name='cat',
            field=models.ForeignKey(related_name='job_cat', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Category', to='jobs.Category', null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='sub_cat',
            field=models.ForeignKey(related_name='job_subcat', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Sub Category', to='jobs.Category', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set([('slug', 'parent')]),
        ),
    ]
