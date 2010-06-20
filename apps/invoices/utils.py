import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from site_settings.utils import get_setting
from base.utils import tcurrency
from perms.utils import is_admin

def invoice_html_display(request, invoice, **kwargs):
    my_display = ""
    if invoice.invoice_object_type == 'make_payment':
        my_display = invoice_makepayments_display(request, invoice)
    return my_display

def invoice_makepayments_display(request, invoice, **kwargs):
    from make_payments.models import MakePayment
    try:
        mp = MakePayment.objects.get(pk=invoice.invoice_object_type_id)
    except MakePayment.DoesNotExist:
        mp = None
        
    mystr = "<div class=\"invoice-view-wrap\">"
    
    if invoice.is_tendered:
        mystr += "<span>TENDERED: "
        if isinstance(invoice.tender_date, datetime.datetime):
            mystr += invoice.tender_date.strftime('%b %d, %Y %H:%M %p')
        mystr += '</span>'
        if is_admin(request.user) and invoice.balance > 0:
            # need to add link here for admin to verify payment
            mystr += "&nbsp;<a href=\"\" class=\"body_copy_yellow\">Admin: Receive or Verify Payment</a>"
    else:
        mystr += "<div class=\"subtitles\">"
        mystr += "E-S-T-I-M-A-T-E &nbsp;&nbsp;"
        mystr += "</div>"
        
    mystr += "<div class=\"invoice-view-box\">"   
    mystr += invoice_makepayments_user_info(invoice, mp)
    mystr += "</div>"
    
    mystr += "<div class=\"invoice-view-box\">"   
    mystr += invoice_totals_info(invoice)
    mystr += "</div>"
    
    if invoice.balance > 0 and hasattr(settings, 'MERCHANT_LOGIN') and settings.MERCHANT_LOGIN:
        # link to payonline
        mystr += "<div class=\"invoice-view-box\">"   
        mystr += "<div class=\"invoice-view-payonline\">"
        mystr += "<a href=\"" + reverse('payments.views.pay_online', args=[invoice.id, invoice.guid])
        mystr += "\" class=\"body_copy_yellow\" title=\"Pay Online\">Pay Online Now</a>"
        mystr += "</div>"
        mystr += "<div class=\"clear-right\"></div>"
        mystr += "</div>"
    
    mystr += "</div>"
    
    # display payment history
    payment_history = payment_history_by_invoice(invoice)
    if payment_history <> "":
        mystr += payment_history
    
    return mystr
          
def invoice_makepayments_user_info(invoice, make_payment, **kwargs):
    mp = make_payment
    mystr = ""
    if mp:
        tmp_name = "Payment Made by %s %s" % (mp.first_name, mp.last_name)
    else:
        tmp_name = "Make Payment Information not available"
        
    # make 3 blocks in the first box
    mystr += "<div class=\"invoice-view-detail-left\">"
    # block #1 - make_payment_id
    if mp: 
        mystr += "<a href=\"%s\" title=\"View Make Payment\">%d</a>" % \
                (reverse('make_payment.view', args=[invoice.invoice_object_type_id]), mp.id)
    else:
        mystr += str(invoice.invoice_object_type_id)
    mystr += "</div>"
    
    # block #2 - make_payment details
    mystr += "<div class=\"invoice-view-detail-middle\">"
    mystr += "<div class=\"invoice-item\">%s</div>" % tmp_name
    mystr += "<div class=\"invoice-item\">Phone: %s</div>" % mp.phone
    mystr += "<div class=\"invoice-item\">Email: %s</div>" % mp.email
    if mp.company:
        mystr += "<div class=\"invoice-item\">Company: %s</div>" % mp.company
    if mp.address or mp.address or mp.city or mp.state or mp.zip_code:
        mystr += "<div class=\"invoice-item\">Address: %s %s %s %s %s</div>" % (mp.address, mp.address2, mp.city, mp.state, mp.zip_code)
    mystr += "</div>"
    
    # block #3 - amount
    mystr += "<div class=\"invoice-view-detail-right\">"
    mystr += "Amount: %s" % (tcurrency(invoice.total))
    mystr += "</div>"
    
    mystr += "<div class=\"clear-both\"></div>"
    
    return mystr


def invoice_totals_info(invoice, **kwargs):
    mystr = ""
    
    mystr += "<div class=\"invoice-view-totals\">"
    mystr += "<div class=\"invoice-item\">Totals</div>"
    mystr += "<div class=\"invoice-item\">Sub Total: %s</div>" % (tcurrency(invoice.subtotal))
    mystr += "<div class=\"invoice-item\">Total: %s</div>" % (tcurrency(invoice.total))
    mystr += "<div class=\"invoice-item\">Payments/Credits: %s</div>" % (tcurrency(invoice.payments_credits))
    mystr += "<div class=\"invoice-item\">Balance due: %s</div>" % (tcurrency(invoice.balance))
    if invoice.balance <= 0:
        if invoice.payment_set:
            payment = invoice.payment_set.order_by('-id')[0]
            mystr += "<div class=\"invoice-item\">Payment method: %s</div>" % (payment.method)
    mystr += "</div>"
    
    mystr += "<div class=\"clear-right\"></div>"
    return mystr


def payment_history_by_invoice(invoice, **kwargs):
    payments = invoice.payment_set.order_by('-id')
    mystr = ""
    if payments:
        for payment in payments:
            mystr += payment_row_display(payment)
    return mystr

def payment_row_display(payment, **kwargs):
    mystr = ""
    
    display_class = ""
    if payment.is_paid:
        if payment.amount < 0:
            display_class = "body_copy_alerts"
    else:
        if payment.status_detail == 'void':
            display_class = "body_copy_gray"
        else:
            display_class = "body_copy_yellow"
    print display_class   
    mystr += "<div class=\"invoice-view-payment-wrap %s\">"  % (display_class) 
    # make 3 blocks in the payment box
    mystr += "<div class=\"invoice-view-detail-left\">"
    # block #1 - make_payment_id
    mystr += "<a href=\"link to view payment\" title=\"View Payment\">%d</a>" % (payment.id)
    mystr += "</div>"
    
    # block #2 - payment transaction details
    mystr += "<div class=\"invoice-view-detail-middle\">"
    mystr += "<div class=\"invoice-item\">%s, %s</div>" % (payment.last_name, payment.first_name)
    if payment.creator:
        mystr += "<div class=\"invoice-item\">Creator: <a href=\"%s\">%s</a></div>" % \
        (payment.creator.get_absolute_url(), payment.creator_username)
    if payment.trans_id and payment.trans_id <> '0':
        mystr += "<div class=\"invoice-item\">Trans_ID: %s</div>" %  payment.trans_id
    else:
        if payment.trans_string and payment.trans_string <> '':
            mystr += "<div class=\"invoice-item\">Trans_String: %s</div>" %  payment.trans_string
        else:
            mystr += "<div class=\"invoice-item\">Trans_ID not available</div>" 
    if payment.response_reason_text and payment.response_reason_text <> '':
        mystr += "<div class=\"invoice-item\">%s</div>" % (payment.response_reason_text)
    mystr += "<div class=\"invoice-item\">%s</div>" % (payment.description)
    mystr += "</div>"
    
    # block #3 -payment status
    mystr += "<div class=\"invoice-view-detail-right\">"
    mystr += "<div class=\"invoice-item\">%s</div>" % (payment.create_dt.strftime('%b %d, %Y %H:%M %p'))
    mystr += "<div class=\"invoice-item\">Invoice: <a href=\"%s\">%d</a></div>" % \
            (reverse('invoices.view', args=[payment.invoice.id]), payment.invoice.id)

    if not payment.status_detail or  payment.status_detail == '':
        if not payment.verified:
            payment_status = "ABANDON"
        else:
            payment_status = "Verified, Not Received"
    else:
        if payment.status_detail == 'void':
            payment_status = "VOID"
        else:
            payment_status = payment.status_detail
    mystr += "<div class=\"invoice-item\">[Payment Status: %s]</div>" % (payment_status)
    blank_status_detail = ''
    if not payment.status_detail or payment.status_detail== '':
        blank_status_detail = '**'
    mystr += "<div class=\"invoice-item\">%s %s%s</div>" % (payment.method, tcurrency(payment.amount), blank_status_detail)
    mystr += "</div>"
    
    mystr += "<div class=\"clear-both\"></div>"
    
    mystr += "</div>"
    
    return mystr
    
        