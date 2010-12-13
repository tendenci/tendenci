from django.template import Library

register = Library()

@register.inclusion_tag("payments/thankyou_display.html", takes_context=True)
def payment_thankyou_display(context, payment, obj_d):
    context.update({
        "payment" : payment,
        "obj_d": obj_d
    })
    return context