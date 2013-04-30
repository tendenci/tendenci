from django.template import Library

register = Library()


@register.inclusion_tag("accountings/acct_entry_item.html", takes_context=True)
def acct_entry_item(context, acct_entry, entry_class=''):
    #from tendenci.apps.accountings.models import AcctTran
    acct_trans = acct_entry.trans.all()

    # calculate the total_debit and total_credit and update the context
    for acct_tran in acct_trans:
        if acct_tran.amount > 0:
            context['total_debit'] += acct_tran.amount
        if acct_tran.amount < 0:
            context['total_credit'] += abs(acct_tran.amount)
    context.update({
        'acct_trans': acct_trans,
        'entry_class': entry_class
    })

    return context
