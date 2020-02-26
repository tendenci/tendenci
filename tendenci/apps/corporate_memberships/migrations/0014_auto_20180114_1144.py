# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        ('corporate_memberships', '0013_auto_20171207_1558'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='corpmembership',
            options={'verbose_name': 'Corporate Membership', 'verbose_name_plural': 'Corporate Memberships'},
        ),
        migrations.AlterModelOptions(
            name='corpmembershipapp',
            options={'ordering': ('name',), 'verbose_name': 'Corporate Membership Application', 'verbose_name_plural': 'Corporate Membership Application'},
        ),
        migrations.AlterModelOptions(
            name='corpmembershipappfield',
            options={'ordering': ('position',), 'verbose_name': 'Membership Application Field', 'verbose_name_plural': 'Membership Application Fields'},
        ),
        migrations.AlterModelOptions(
            name='corpmembershiprep',
            options={'verbose_name': 'Corporate Membership Representative', 'verbose_name_plural': 'Corporate Membership Representatives'},
        ),
        migrations.AlterModelOptions(
            name='corporatemembershiptype',
            options={'verbose_name': 'Corporate Membership Type', 'verbose_name_plural': 'Corporate Membership Types'},
        ),
        migrations.AlterModelOptions(
            name='corpprofile',
            options={'verbose_name': 'Corporate Member Profile', 'verbose_name_plural': 'Corporate Member Profiles'},
        ),
        migrations.AlterModelOptions(
            name='notice',
            options={'verbose_name': 'Member Notice', 'verbose_name_plural': 'Member Notices'},
        ),
        migrations.AddField(
            model_name='corpmembershipapp',
            name='dues_reps_group',
            field=models.ForeignKey(related_name='dues_reps_group', on_delete=django.db.models.deletion.SET_NULL, to='user_groups.Group', help_text='Dues reps will be added to this group', null=True),
        ),
        migrations.AddField(
            model_name='corpmembershipapp',
            name='member_reps_group',
            field=models.ForeignKey(related_name='member_reps_group', on_delete=django.db.models.deletion.SET_NULL, to='user_groups.Group', help_text='Member reps will be added to this group', null=True),
        ),
    ]
