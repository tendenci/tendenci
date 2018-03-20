from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.accountings.models import Acct


def account_numbers(request, template_name="accountings/account_numbers.html"):
    accts = Acct.objects.all().order_by('account_number')
    return render_to_resp(request=request, template_name=template_name,
                          context={'accts': accts})
