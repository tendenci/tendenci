from builtins import str
import os
from django.db.models import Max, Count
from celery.task import Task
from tendenci.apps.exports.utils import full_model_to_dict, render_csv
from tendenci.apps.navs.models import Nav
from tendenci.apps.base.utils import escape_csv

class NavsExportTask(Task):
    """Export Task for Celery
    This exports all navs data and nav items.
    """

    def run(self, **kwargs):
        """Create the xls file"""
        nav_fields = [
            'title',
            'description',
            'megamenu',
            'allow_anonymous_view',
            'allow_user_view',
            'allow_member_view',
            'allow_user_edit',
            'allow_member_edit',
            'create_dt',
            'update_dt',
            'creator',
            'creator_username',
            'owner',
            'owner_username',
            'status',
            'status_detail',
        ]
        nav_item_fields = [
            'label',
            'title',
            'new_window',
            'css',
            'position',
            'level',
            'page',
            'url',
        ]

        navs = Nav.objects.filter(status=True)
        max_nav_items = navs.annotate(num_navitems=Count('navitem')).aggregate(Max('num_navitems'))['num_navitems__max']
        file_name = 'navs.csv'
        data_row_list = []

        for nav in navs:
            data_row = []
            # nav setup
            nav_d = full_model_to_dict(nav)
            for field in nav_fields:
                value = nav_d[field]
                value = str(value).replace(os.linesep, ' ').rstrip()
                value = escape_csv(value)
                data_row.append(value)

            if nav.navitem_set.all():
                # nav_item setup
                for nav_item in nav.navitem_set.all():
                    nav_item_d = full_model_to_dict(nav_item)
                    for field in nav_item_fields:
                        value = nav_item_d[field]
                        value = str(value).replace(os.linesep, ' ').rstrip()
                        value = escape_csv(value)
                        data_row.append(value)

            # fill out the rest of the nav_item columns
            if nav.navitem_set.all().count() < max_nav_items:
                for i in range(0, max_nav_items - nav.navitem_set.all().count()):
                    for field in nav_item_fields:
                        data_row.append('')

            data_row_list.append(data_row)

        fields = nav_fields
        for i in range(0, max_nav_items):
            fields = fields + ["nav_item %s %s" % (i, f) for f in nav_item_fields]
        return render_csv(file_name, fields, data_row_list)
