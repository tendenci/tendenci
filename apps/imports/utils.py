import os
import datetime

from django.db import models
from django.http import HttpResponse

import xlrd
from xlwt import Workbook, XFStyle

def handle_uploaded_file(f, file_path):
    destination = open(file_path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

def render_excel(filename, col_title_list, data_row_list):
    import StringIO
    output = StringIO.StringIO()
    export_wb = Workbook()
    export_sheet = export_wb.add_sheet('Sheet1')
    col_idx = 0
    for col_title in col_title_list:
        export_sheet.write(0, col_idx, col_title)
        col_idx += 1
    row_idx = 1
    for row_item_list in data_row_list:
        col_idx = 0
        for current_value in row_item_list:
            if current_value:
                current_value_is_date = False
                if isinstance(current_value, datetime.datetime):
                    current_value = xlrd.xldate.xldate_from_datetime_tuple((current_value.year, current_value.month, \
                                                    current_value.day, current_value.hour, current_value.minute, \
                                                    current_value.second), 0)
                    current_value_is_date = True
                elif isinstance(current_value, datetime.date):
                    current_value = xlrd.xldate.xldate_from_date_tuple((current_value.year, current_value.month, \
                                                    current_value.day), 0)
                    current_value_is_date = True
                elif isinstance(current_value, datetime.time):
                    current_value = xlrd.xldate.xldate_from_time_tuple((current_value.hour, current_value.minute, \
                                                    current_value.second))
                    current_value_is_date = True
                elif isinstance(current_value, models.Model):
                    current_value = str(current_value)
                if current_value_is_date:
                    s = XFStyle()
                    s.num_format_str = 'M/D/YY'
                    export_sheet.write(row_idx, col_idx, current_value, s)
                else:
                    export_sheet.write(row_idx, col_idx, current_value)
            col_idx += 1
        row_idx += 1
    export_wb.save(output)
    output.seek(0)
    response = HttpResponse(output.getvalue())
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = 'attachment; filename='+filename
    return response