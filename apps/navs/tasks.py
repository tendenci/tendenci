import os
from django.forms.models import model_to_dict
from django.db.models import Avg, Max, Min, Count
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.contrib.contenttypes import generic
from django.forms.models import model_to_dict
from celery.task import Task
from celery.registry import tasks
from imports.utils import render_excel
from navs.models import Nav

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
        ]
        nav_item_fields = [
            'label',
            'title',
            'new_window',
            'css',
            'ordering',
            'level',
            'page',
            'url',
        ]
        
        navs = Nav.objects.filter(status=1)
        max_nav_items = navs.annotate(num_navitems=Count('navitem')).aggregate(Max('num_navitems'))['num_navitems__max']
        file_name = 'navs.xls'
        data_row_list = []
        
        for nav in navs:
            data_row = []
            # nav setup
            nav_d = model_to_dict(nav)
            for field in nav_fields:
                value = nav_d[field]
                value = unicode(value).replace(os.linesep, ' ').rstrip()
                data_row.append(value)
            
            if nav.navitem_set.all():
                # nav_item setup
                for nav_item in nav.navitem_set.all():
                    nav_item_d = model_to_dict(nav_item)
                    for field in nav_item_fields:
                        value = nav_item_d[field]
                        value = unicode(value).replace(os.linesep, ' ').rstrip()
                        data_row.append(value)
            
            # fill out the rest of the nav_item columns
            if nav.navitem_set.all().count() < max_nav_items:
                for i in range(0, max_nav_items - nav.navitem_set.all().count()):
                    for field in nav_item_fields:
                        data_row.append('')
            
            data_row.append('\n') # append a new line to make a new row
            data_row_list.append(data_row)
        
        fields = nav_fields
        for i in range(0, max_nav_items):
            fields = fields + ["nav_item %s %s" % (i, f) for f in nav_item_fields]
        fields.append('\n')
        return render_excel(file_name, fields, data_row_list)
