from django.template import Library

register = Library()

@register.inclusion_tag("invoices/invoice_item.html")
def invoices_search_results_line(request, invoice):
    item_display = ""
    if invoice.invoice_object_type == 'make_payment':
        item_display = invoices_display_make_payments(request, invoice)
    return {"item_display": item_display}


def invoices_display_make_payments(request, invoice):
    from make_payments.models import MakePayment
    mystr = ""
    try:
        mp = MakePayment.objects.get(id=invoice.invoice_object_type_id)
    except MakePayment.DoesNotExist:
        mp = None
        
def invoices_display_top_row(invoice):
    return ""
    
    
    