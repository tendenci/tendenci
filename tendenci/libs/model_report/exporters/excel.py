# -*- coding: utf-8 -*-
from xlwt import Workbook, easyxf

from django.http import HttpResponse

from tendenci.libs.model_report import arial10
from .base import Exporter


class FitSheetWrapper(object):
    """Try to fit columns to max size of any entry.
    To use, wrap this around a worksheet returned from the
    workbook's add_sheet method, like follows:

        sheet = FitSheetWrapper(book.add_sheet(sheet_name))

    The worksheet interface remains the same: this is a drop-in wrapper
    for auto-sizing columns.
    """
    def __init__(self, sheet):
        self.sheet = sheet
        self.widths = dict()
        self.heights = dict()

    def write(self, r, c, label='', *args, **kwargs):
        self.sheet.write(r, c, label, *args, **kwargs)
        self.sheet.row(r).collapse = True
        bold = False
        if args:
            style = args[0]
            bold = str(style.font.bold) in ('1', 'true', 'True')
        width = int(arial10.fitwidth(label, bold))
        if width > self.widths.get(c, 0):
            self.widths[c] = width
            self.sheet.col(c).width = width

        height = int(arial10.fitheight(label, bold))
        if height > self.heights.get(r, 0):
            self.heights[r] = height
            self.sheet.row(r).height = height

    def __getattr__(self, attr):
        return getattr(self.sheet, attr)


class ExcelExporter(Exporter):

    @classmethod
    def render(cls, report, column_labels, report_rows, report_inlines):
        book = Workbook(encoding='utf-8')
        sheet1 = FitSheetWrapper(book.add_sheet(report.get_title()[:20]))
        stylebold = easyxf('font: bold true; alignment:')
        stylevalue = easyxf('alignment: horizontal left, vertical top;')
        row_index = 0
        for index, x in enumerate(column_labels):
            sheet1.write(row_index, index, u'%s' % x, stylebold)
        row_index += 1

        for g, rows in report_rows:
            if g:
                sheet1.write(row_index, 0, u'%s' % g, stylebold)
                row_index += 1
            for row in list(rows):
                if row.is_value():
                    for index, x in enumerate(row):
                        if isinstance(x.value, (list, tuple)):
                            xvalue = ''.join(['%s\n' % v for v in x.value])
                        else:
                            xvalue = x.text()
                        sheet1.write(row_index, index, xvalue, stylevalue)
                    row_index += 1
                elif row.is_caption:
                    for index, x in enumerate(row):
                        if not isinstance(x, (unicode, str)):
                            sheet1.write(row_index, index, x.text(), stylebold)
                        else:
                            sheet1.write(row_index, index, x, stylebold)
                    row_index += 1
                elif row.is_total:
                    for index, x in enumerate(row):
                        sheet1.write(row_index, index, x.text(), stylebold)
                        sheet1.write(row_index + 1, index, ' ')
                    row_index += 2

        response = HttpResponse(content_type="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % report.slug
        book.save(response)
        return response
