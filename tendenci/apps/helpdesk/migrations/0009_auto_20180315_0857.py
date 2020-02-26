# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk', '0008_auto_20160121_1222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queue',
            name='socks_proxy_type',
            field=models.CharField(choices=[('socks4', 'SOCKS4'), ('socks4', 'SOCKS5')], max_length=8, blank=True, help_text='SOCKS4 or SOCKS5 allows you to proxy your connections through a SOCKS server.', null=True, verbose_name='Socks Proxy Type'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='creator_username',
            field=models.CharField(default='', max_length=50, editable=False),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='owner',
            field=models.ForeignKey(related_name='helpdesk_ticket_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, help_text='You should assign a client to the owner so he/she can update the ticket.', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='ticketcustomfieldvalue',
            unique_together=set([('ticket', 'field')]),
        ),
    ]
