from django.core.urlresolvers import reverse
from site_settings.utils import get_setting
siteurl = get_setting('site', 'global', 'siteurl')

# update the object
def payment_processing_object_updates(payment, **kwargs):
    # process based on invoice object type - needs lots of work here.
    pass

# return the display message on the thankyou page
def payment_processing_thankyou_display(payment, **kwargs):
    # display based on invoice object type - needs lots of work here
    display_html = "<h1>Payment Status</h1>"
    display_html += payment_processing_status_text(payment)
    display_html += "<p>&nbsp;</p>\n" 
    display_html += payment_processing_payment_invoice_callstoaction(payment)
    display_html += "<p>&nbsp;</p>\n" 
    display_html += "<p>&nbsp;</p>\n" 
    
    return display_html

def payment_processing_status_text(payment, **kwargs):
    msg = "<p>&nbsp;</p>" + '\n'
    msg += "<p>" + '\n'
    if not payment.is_approved:
        msg += "<b>" + '\n'
        msg += "DO NOT press the back button in your browser."  + '\n'
        msg += "</b>" + '\n'
        msg += "<a href=\"%s%s\">Try Making Payment Again</a>\n" % \
                (siteurl,reverse('invoice.view', args=[payment.invoice.id]))
    else:
        msg += "<b>" + '\n'
        msg += "DO NOT press the back button in your browser, or your credit card will be charged twice." + '\n'
        msg += "</b>" + '\n'
    msg += "</p>" + '\n'
    msg += "<p>&nbsp;</p>" + '\n'
    msg += "<p>Status of transaction (with reason if declined):</p>" + '\n'
    msg += "<b>" + '\n'
    msg += payment.response_reason_text + '\n'
    msg += "</b>"  + '\n'
    msg += "<b>"  + '\n'
    msg += payment.response_reason_text  + '\n'
    msg += "</b>"  + '\n'
    msg += "<p>&nbsp;</p>"  + '\n'
    
    return msg

def payment_processing_payment_invoice_callstoaction(payment, **kwargs):
    if not payment.is_approved:
        msg = "<p>" + '\n'
        msg += "<a href=\"%s%s\">Try Making Payment Again</a>\n"  % (siteurl,reverse('invoice.view', args=[payment.invoice.id]))
        msg += "</p>" + '\n'
    else:
        msg = "<p>" + '\n'
        msg += "<a href="">Print Friendly Invoice.</a>" + '\n'
        msg += "</p>" + '\n'
        msg += "<p><a href=\"%s%s\">View my Invoice</a></p>\n" % (siteurl, reverse('invoice.view', args=[payment.invoice.id]))
        msg += "<p>Thank you for your payment!</p>"  + '\n'
   
    msg += "<p>&nbsp;</p>"  + '\n'
    
    return msg