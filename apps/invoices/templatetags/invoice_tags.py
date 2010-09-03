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
        
        try:
            mp = MakePayment.objects.get(id=invoice.invoice_object_type_id)
        except MakePayment.DoesNotExist:
            mp = None
        return {'request':request, 'invoice':invoice, 'mp':mp}
    elif invoice.invoice_object_type == 'event_registration':
        from events.models import Registration
        
        try:
            reg8n = Registration.objects.get(id=invoice.invoice_object_type_id)
        except Registration.DoesNotExist:
            reg8n = None
        return {'request':request, 'invoice':invoice, 'reg8n':reg8n}
    elif invoice.invoice_object_type == 'job':
        from jobs.models import Job
        
        try:
            job = Job.objects.get(id=invoice.invoice_object_type_id)
        except Job.DoesNotExist:
            job = None
        return {'request':request, 'invoice':invoice, 'job':job}
    elif invoice.invoice_object_type == 'directory':
        from directories.models import Directory
        
        try:
            directory = Directory.objects.get(id=invoice.invoice_object_type_id)
        except Directory.DoesNotExist:
            directory = None
        return {'request':request, 'invoice':invoice, 'directory':directory}
    elif invoice.invoice_object_type == 'donation':
        from donations.models import Donation
        
        try:
            donation = Donation.objects.get(id=invoice.invoice_object_type_id)
        except Donation.DoesNotExist:
            donation = None
        return {'request':request, 'invoice':invoice, 'donation':donation}
    else:
        return {'request':request, 'invoice':invoice}
 
 
@register.inclusion_tag("invoices/search_line_header.html")
def invoices_search_line_header(request, invoice, obj_color):
    return {'request':request, 'invoice':invoice, 'obj_color':obj_color}
       
    
@register.inclusion_tag("invoices/search-form.html", takes_context=True)
def invoice_search(context):
    return context

# display make_payment on invoice view
@register.inclusion_tag("invoices/makepayment_display.html")
def invoice_makepayments_display(request, invoice):
    from make_payments.models import MakePayment
    #item_display = invoices_display_make_payments(request, invoice)
    try:
        mp = MakePayment.objects.get(id=invoice.invoice_object_type_id)
    except MakePayment.DoesNotExist:
        mp = None
    return {'request':request, 'invoice':invoice, 'mp':mp}

# display event registration on invoice view
@register.inclusion_tag("invoices/event_display.html")
def invoice_event_display(request, invoice):
    from events.models import Registration
    #item_display = invoices_display_make_payments(request, invoice)
    try:
        reg8n = Registration.objects.get(id=invoice.invoice_object_type_id)
    except Registration.DoesNotExist:
        reg8n = None
    return {'request':request, 'invoice':invoice, 'reg8n':reg8n}

# display job on invoice view
@register.inclusion_tag("invoices/job_display.html")
def invoice_job_display(request, invoice):
    from jobs.models import Job
    #item_display = invoices_display_make_payments(request, invoice)
    try:
        job = Job.objects.get(id=invoice.invoice_object_type_id)
    except Job.DoesNotExist:
        job = None
    return {'request':request, 'invoice':invoice, 'job':job}

# display directory on invoice view
@register.inclusion_tag("invoices/directory_display.html")
def invoice_directory_display(request, invoice):
    from directories.models import Directory
    #item_display = invoices_display_make_payments(request, invoice)
    try:
        directory = Directory.objects.get(id=invoice.invoice_object_type_id)
    except Directory.DoesNotExist:
        directory = None
    return {'request':request, 'invoice':invoice, 'directory':directory}

# display donation on invoice view
@register.inclusion_tag("invoices/donation_display.html")
def invoice_donation_display(request, invoice):
    from donations.models import Donation
    #item_display = invoices_display_make_payments(request, invoice)
    try:
        donation = Donation.objects.get(id=invoice.invoice_object_type_id)
    except Donation.DoesNotExist:
        donation = None
    return {'request':request, 'invoice':invoice, 'donation':donation}


# display invoice total on invoice view
@register.inclusion_tag("invoices/total_display.html")
def invoice_total_display(request, invoice):
    tmp_total = 0
    if invoice.variance and invoice.variance <> 0:
        tmp_total = invoice.subtotal
        if invoice.tax:
            tmp_total += invoice.tax
        if invoice.shipping:
            tmp_total += invoice.shipping
        if invoice.shipping_surcharge:
            tmp_total += invoice.shipping_surcharge
        if invoice.box_and_packing:
            tmp_total += invoice.box_and_packing
            
    payment_method = ""
    if invoice.balance <= 0:
        if invoice.payment_set:
            payment_set = invoice.payment_set.order_by('-id')
            if payment_set:
                payment = payment_set[0]
                payment_method = payment.method
                
    return {'request':request, 'invoice':invoice, 'tmp_total':tmp_total, 'payment_method':payment_method}

# display payment history on invoice view
@register.inclusion_tag("invoices/payment_history.html")
def payment_history_display(request, invoice):
    payments = invoice.payment_set.order_by('-id')

    return {'request':request,
            'invoice':invoice,
            'payments': payments}

        
    
    