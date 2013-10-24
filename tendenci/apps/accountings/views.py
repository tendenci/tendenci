from django.template import RequestContext
from django.shortcuts import render_to_response

from tendenci.apps.accountings.models import Acct


def account_numbers(request, template_name="accountings/account_numbers.html"):
    accts = Acct.objects.all().order_by('account_number')
    return render_to_response(template_name, {'accts': accts, },
                              context_instance=RequestContext(request))
