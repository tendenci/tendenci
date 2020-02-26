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
            name='Acct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account_number', models.IntegerField(unique=True)),
                ('description', models.TextField()),
                ('type', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='AcctEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.TextField()),
                ('object_id', models.IntegerField()),
                ('entry_dt', models.DateTimeField(auto_now_add=True)),
                ('exported', models.BooleanField(default=False)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('creator_username', models.CharField(default='', max_length=50)),
                ('owner_username', models.CharField(default='', max_length=50)),
                ('status', models.BooleanField(default=True)),
                ('creator', models.ForeignKey(related_name='accentry_creator', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('owner', models.ForeignKey(related_name='accentry_owner', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AcctTran',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2, blank=True)),
                ('cleared', models.BooleanField(default=False)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=True)),
                ('account', models.ForeignKey(related_name='accts', to='accountings.Acct', null=True, on_delete=django.db.models.deletion.CASCADE)),
                ('acct_entry', models.ForeignKey(related_name='trans', to='accountings.AcctEntry', on_delete=django.db.models.deletion.CASCADE)),
                ('creator', models.ForeignKey(related_name='accttran_creator', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('owner', models.ForeignKey(related_name='accttran_owner', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
