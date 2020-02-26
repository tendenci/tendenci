# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('helpdesk', '0007_max_length_by_integer'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='creator',
            field=models.ForeignKey(related_name='helpdesk_ticket_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='creator_username',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='ticket',
            name='owner',
            field=models.ForeignKey(related_name='helpdesk_ticket_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='owner_username',
            field=models.CharField(default='', max_length=50),
        ),
    ]
