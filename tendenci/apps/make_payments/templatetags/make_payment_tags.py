from django.template import Library


register = Library()


@register.inclusion_tag("make_payments/nav.html", takes_context=True)
def make_payment_nav(context, make_payment=None):
    context.update({
        "nav_object" : make_payment,
    })
    return context


@register.inclusion_tag("make_payments/top_nav_items.html", takes_context=True)
def make_payment_current_app(context, make_payment=None):
    context.update({
        "app_object" : make_payment,
    })
    return context
