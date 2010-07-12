from django.template import Library

register = Library()


@register.inclusion_tag("invoices/nav.html", takes_context=True)
def invoice_nav(context, invoice=None):
    context.update({
        "nav_object" : invoice,
    })
    return context

@register.inclusion_tag("invoices/invoice_item.html")
def invoices_search_results_line(request, invoice):
    if invoice.invoice_object_type == 'make_payment':
        from make_payments.models import MakePayment
        #item_display = invoices_display_make_payments(request, invoice)
        try:
            mp = MakePayment.objects.get(id=invoice.invoice_object_type_id)
        except MakePayment.DoesNotExist:
            mp = None
        return {'request':request, 'invoice':invoice, 'mp':mp}
    else:
        return {'request':request, 'invoice':invoice}
    
    
@register.inclusion_tag("invoices/search-form.html", takes_context=True)
def invoice_search(context):
    return context


        
    
    