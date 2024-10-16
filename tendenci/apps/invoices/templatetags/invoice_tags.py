from django.template import Library
from django.conf import settings

from tendenci.apps.site_settings.utils import get_setting

register = Library()


@register.inclusion_tag("invoices/nav.html", takes_context=True)
def invoice_nav(context, invoice=None):
    context.update({
        "nav_object": invoice,
    })
    return context


@register.inclusion_tag("invoices/invoice_item.html")
def invoices_search_results_line(request, invoice):
    obj = invoice.get_object()
    object_display = invoice.object_display(obj=obj)
        

    # search_line_display = None
    # if invoice.object_type:
    #     from django.template.loader import render_to_string
    #     from django.template import TemplateDoesNotExist
    #
    #     app_label = invoice.object_type.app_label
    #     template_name = "%s/invoice_search_result_line.html" % (app_label)
    #     try:
    #         search_line_display = render_to_string(
    #             template_name=template_name,
    #             context={'obj':obj,'invoice':invoice},
    #             request=request
    #         )
    #     except (TemplateDoesNotExist, IOError):
    #         pass

    return {'request':request, 'invoice':invoice, 'obj':obj, 'object_display': object_display}


@register.inclusion_tag("invoices/search_line_header.html", takes_context=True)
def invoices_search_line_header(context, request, invoice, obj_color):
    context.update({'request': request,
                   'invoice': invoice,
                   'obj_color': obj_color})
    return context


@register.inclusion_tag("invoices/search-form.html", takes_context=True)
def invoice_search(context):
    return context


@register.inclusion_tag("invoices/top_nav_items.html", takes_context=True)
def invoice_current_app(context, user, invoice=None):
    context.update({
        "app_object": invoice,
        "user": user
    })
    return context


# display object on invoice view
@register.inclusion_tag("invoices/object_display.html")
def invoice_object_display(request, invoice):
    obj = invoice.get_object()
    object_display = None

    if invoice.object_type:
        from django.template.loader import render_to_string
        from django.template import TemplateDoesNotExist

        app_label = invoice.object_type.app_label
        model = invoice.object_type.model
        # since membership app has 2 different associated invoices
        if app_label == 'memberships' and model == 'membershipset':
            template_name = "%s/invoice_view_display2.html" % (app_label)
        elif app_label == 'events' and model == 'assetspurchase':
            template_name = "%s/invoice_view_display_assetspurchase.html" % (app_label)
        else:
            template_name = "%s/invoice_view_display.html" % (app_label)
        try:
            object_display = render_to_string(
                template_name=template_name,
                context={'obj': obj, 'invoice': invoice},
                request=request
            )
        except (TemplateDoesNotExist, IOError):
            pass

    context = {
        'request': request,
        'invoice': invoice,
        'obj': obj,
        'object_display': object_display
    }
    return context

# display invoice total on invoice view
@register.inclusion_tag("invoices/total_display.html", takes_context=True)
def invoice_total_display(context, request, invoice):
    tmp_total = 0
    payment_method = ""

    if invoice.variance and invoice.variance != 0:
        tmp_total = invoice.subtotal
        if invoice.tax:
            tmp_total += invoice.tax
        if invoice.shipping:
            tmp_total += invoice.shipping
        if invoice.shipping_surcharge:
            tmp_total += invoice.shipping_surcharge
        if invoice.box_and_packing:
            tmp_total += invoice.box_and_packing

    if invoice.balance <= 0:
        if invoice.payment_set:
            payment_set = invoice.payment_set.order_by('-id')
            if payment_set:
                payment = payment_set[0]
                payment_method = payment.method
                if payment.check_number:
                    payment_method = f'{payment_method} ({payment.check_number})'

    merchant_login = get_setting("site", "global", "merchantaccount") != 'asdf asdf asdf'

    context.update({
        'request': request,
        'invoice': invoice,
        'tmp_total': tmp_total,
        'payment_method': payment_method,
        'merchant_login': merchant_login
    })
    return context

# display payment history on invoice view
@register.inclusion_tag("invoices/payment_history.html")
def payment_history_display(request, invoice):
    payments = invoice.payment_set.order_by('-id')
    refunds = invoice.refund_set.order_by('-id')

    return {'request':request,
            'invoice':invoice,
            'payments': payments,
            'refunds': refunds}
