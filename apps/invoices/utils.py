

def invoice_html_display(request, invoice, **kwargs):
    my_display = ""
    if invoice.invoice_object_type == 'make_payment':
        my_display = ""
    return my_display