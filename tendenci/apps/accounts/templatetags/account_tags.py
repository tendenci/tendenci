from django.template import Library
from tendenci.apps.accounts.forms import LoginForm

register = Library()

@register.inclusion_tag("accounts/login_form.html", takes_context=True)
def login_form(context, login_button_value=None):
    form = LoginForm()
    context.update({
        'form': form,
        'login_button_value': login_button_value
    })
    return context