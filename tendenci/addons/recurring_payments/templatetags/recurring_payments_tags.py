from django.template import Library, TemplateSyntaxError, Variable

from tendenci.addons.recurring_payments.models import RecurringPayment

register = Library()


@register.inclusion_tag("recurring_payments/nav.html", takes_context=True)
def rp_nav(context, user, rp=None):
    context.update({
        "nav_object": rp,
        "user": user
    })
    return context