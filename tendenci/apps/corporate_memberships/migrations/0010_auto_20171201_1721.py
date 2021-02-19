# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0001_initial'),
        ('corporate_memberships', '0009_auto_20170803_2057'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpprofile',
            name='parent_entity',
            field=models.ForeignKey(blank=True, to='entities.Entity', null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AlterField(
            model_name='corporatemembershiptype',
            name='above_cap_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, blank=True, help_text='Price for members who join above cap.', null=True, verbose_name='Price if join above cap'),
        ),
        migrations.AlterField(
            model_name='corporatemembershiptype',
            name='allow_above_cap',
            field=models.BooleanField(default=False, help_text='If Apply cap is checked, check this box to allow additional members to join above cap.', verbose_name='Allow above cap'),
        ),
        migrations.AlterField(
            model_name='notice',
            name='notice_type',
            field=models.CharField(max_length=20, verbose_name='For Notice Type', choices=[('approve_join', 'Join Approval Date'), ('disapprove_join', 'Join Disapproval Date'), ('join', 'Apply Date'), ('approve_renewal', 'Renewal Approval Date'), ('disapprove_renewal', 'Renewal Disapproval Date'), ('renewal', 'Renewal Date'), ('expiration', 'Expiration Date')]),
        ),
    ]
