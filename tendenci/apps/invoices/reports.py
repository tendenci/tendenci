from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe

from tendenci.libs.model_report.report import reports, ReportAdmin
from tendenci.libs.model_report.utils import (sum_column, us_date_format, date_label, obj_type_format)

from tendenci.apps.invoices.models import Invoice
from tendenci.core.site_settings.utils import get_setting

    
def id_format(value, instance):
    invoice = Invoice.objects.get(id=value)
    link = invoice.get_absolute_url()
    html = "<a href=\"%s\">%s</a>" % (link, value)
    return mark_safe(html)

def currency_format(value, instance):
    currencysymbol = get_setting("site", "global", "currencysymbol")
    return "%s%s" % (currencysymbol, value)

class InvoiceReport(ReportAdmin):
    # choose a title for your report for h1, title tag and report list
    title = _('Invoice Report')
    
    # specify your model
    model = Invoice
    
    # fields in the specified model to display in the report table
    fields = [
        'id',
        'bill_to',
        'create_dt',
        'status_detail',
        'object_type',
        'payments_credits',
        'balance',
        'total'
    ]
    
    # fields in the model to show filters for
    list_filter = ('status_detail', 'create_dt',)
    
    # fields in the model to order results by
    list_order_by = ('create_dt', 'status_detail')
    
    # fields to group results by
    list_group_by = ('object_type',)
    
    # allowed export formats. default is excel and pdf
    exports = ('excel', 'pdf',)
    
    # type = report for report only, type = chart for report and charts. default is report.
    type = 'report'
    
    # override field formats by referencing a function
    override_field_formats = {
        'create_dt': us_date_format,
        'object_type': obj_type_format,
        'id': id_format,
        'balance': currency_format,
        'total': currency_format,
        'payments_credits': currency_format
    }
    
    # override the label for a field by referencing a function
    override_field_labels = {
        'create_dt': date_label
    }
    
    group_totals = {
        'balance': sum_column,
        'total': sum_column,
        'payments_credits': sum_column
    }
    
    report_totals = {
        'balance': sum_column,
        'total': sum_column,
        'payments_credits': sum_column
    }

# register your report with the slug and name
reports.register('invoices', InvoiceReport)