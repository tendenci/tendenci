# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('directories', '0003_auto_20171013_1041'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='directories.Category', null=True, on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.AddField(
            model_name='directory',
            name='cat',
            field=models.ForeignKey(related_name='directory_cat', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Category', to='directories.Category', null=True),
        ),
        migrations.AddField(
            model_name='directory',
            name='sub_cat',
            field=models.ForeignKey(related_name='directory_subcat', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Sub Category', to='directories.Category', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set([('slug', 'parent')]),
        ),
    ]
