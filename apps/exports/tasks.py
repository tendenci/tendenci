import os
from django.forms.models import model_to_dict
from celery.task import Task
from celery.registry import tasks
from imports.utils import render_excel

class TendenciExportTask(Task):
    """Export Task for Celery
    This exports the entire queryset of a given TendenciBaseModel.
    """
    
    def run(self, model, fields, file_name, **kwargs):
        """Create the xls file"""
        items = model.objects.filter(status=1)
        fields.append('\n') # append a new line to mark new row
        data_row_list = []
        for item in items:
            data_row = []
            item_d = model_to_dict(item)
            for field in fields:
                if field != '\n':
                    value = unicode(item_d[field]).replace(os.linesep, ' ').rstrip()
                    data_row.append(value)
            data_row.append('\n')
            data_row_list.append(data_row)
            
        return render_excel(file_name, fields, data_row_list)
