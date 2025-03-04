

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
            field=models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_creator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ticket',
            name='creator_username',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='ticket',
            name='owner',
            field=models.ForeignKey(default=None, help_text='You should assign a client to the owner so he/she can update the ticket.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ticket',
            name='owner_username',
            field=models.CharField(default='', max_length=50),
        ),
    ]
