# -*- coding: utf-8 -*-
class Exporter(object):

    @classmethod
    def render(cls, report, column_labels, report_rows, report_inlines):
        raise NotImplementedError()
