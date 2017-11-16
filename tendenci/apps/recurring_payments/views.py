from datetime import datetime
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
#from django.conf import settings
#from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import simplejson
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.recurring_payments.models import (RecurringPayment,
                                       PaymentProfile,
                                       PaymentTransaction,
                                       RecurringPaymentInvoice)
from tendenci.apps.recurring_payments.authnet.utils import get_test_mode
from tendenci.apps.recurring_payments.utils import (RecurringPaymentEmailNotices,
                                      run_a_recurring_payment)
from tendenci.apps.recurring_payments.authnet.cim import CIMCustomerProfile

from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.base.decorators import ssl_required
from tendenci.apps.base.utils import tcurrency
from tendenci.apps.site_settings.utils import get_setting

@ssl_required
def view_account(request, recurring_payment_id, guid=None,
                          template_name="recurring_payments/index.html"):
    """View a recurring payment account.
    """
    rp = get_object_or_404(RecurringPayment, pk=recurring_payment_id)

    # only admin or user self can access this page
    if not (request.user.is_authenticated() and \
        (request.user.profile.is_superuser \
            or request.user.id == rp.user.id) or rp.guid == guid):
        raise Http403

    paid_payment_transactions = PaymentTransaction.objects.filter(
                                                recurring_payment=rp,
                                                status=True
                                                                )
    if paid_payment_transactions:
        last_paid_payment_transaction = paid_payment_transactions[0]
    else:
        last_paid_payment_transaction = None

    failed_payment_transactions = PaymentTransaction.objects.filter(
                                                recurring_payment=rp,
                                                status=False
                                                                )
    if failed_payment_transactions:
        last_failed_payment_transaction = failed_payment_transactions[0]
    else:
        last_failed_payment_transaction = None

    display_failed_transaction = False
    if last_failed_payment_transaction:
        if not last_paid_payment_transaction or \
            last_failed_payment_transaction.create_dt  \
            > last_paid_payment_transaction.create_dt:
            display_failed_transaction = True

    if not rp.trial_amount:
        rp.trial_amount = 0

    # rp_invoices
    rp_invoices = RecurringPaymentInvoice.objects.filter(
                                        recurring_payment=rp
                                        ).order_by('-billing_cycle_start_dt')

    # payment transactions
    payment_transactions = PaymentTransaction.objects.filter(
                                        recurring_payment=rp
                                        ).order_by('-create_dt')

    # get ready for the add/update payment method button
    test_mode = get_test_mode()
    is_active = (rp.status_detail == 'active')
    if is_active:
        rp.populate_payment_profile()
        payment_profiles = PaymentProfile.objects.filter(
                            customer_profile_id=rp.customer_profile_id,
                            status=True, status_detail='active')
        if payment_profiles:
            payment_profile = payment_profiles[0]
        else:
            payment_profile = None

    else:
        payment_profile = None

    is_owner = False
    if request.user.id == rp.user.id: is_owner = True

    num_accounts = RecurringPayment.objects.filter(user=rp.user).count()

    return render_to_response(template_name, {
                                              'rp': rp,
                                              'display_failed_transaction': display_failed_transaction,
                                              'last_paid_payment_transaction': last_paid_payment_transaction,
                                              'last_failed_payment_transaction': last_failed_payment_transaction,
                                              'rp_invoices': rp_invoices,
                                              'payment_transactions': payment_transactions,
                                              'payment_profile': payment_profile,
                                              'test_mode': test_mode,
                                              'is_active': is_active,
                                              'is_owner': is_owner,
                                              'num_accounts': num_accounts
                                              },
        context_instance=RequestContext(request))

@ssl_required
@login_required
def my_accounts(request, username=None,
                        template_name="recurring_payments/my_accounts.html"):
    """View a person's all recurring payment accounts.
    """
    isadmin = request.user.profile.is_superuser

    if isadmin and username:
        u = get_object_or_404(User, username=username)
    else:
        u = request.user

    #rps = RecurringPayment.objects.filter(user=u).values_list('id', flat=True).order_by('-id')
    rps = RecurringPayment.objects.filter(user=u).order_by('status_detail', '-id')

    if not rps:
        if isadmin:
            return HttpResponseRedirect(reverse('recurring_payment.customers'))
        raise Http404

    if len(rps) == 1:
        # they have only 1 account, go directly to that account
        return  HttpResponseRedirect(reverse('recurring_payment.view_account', args=[(rps[0]).id]))

    is_owner = False
    if request.user.id == u.id: is_owner = True

    return render_to_response(template_name, {'rps': rps,
                                              'is_owner': is_owner,
                                              'account_user': u
                                              },
        context_instance=RequestContext(request))


@staff_member_required
def run_now(request):
    """Run a recurring payment.
    """
    rp_id = request.POST.get('rp_id')
    rp = get_object_or_404(RecurringPayment, pk=rp_id)

    result_data = {}
    result_data['processed'] = 'false'
    result_data['reason'] = 'done'

    payment_profiles = PaymentProfile.objects.filter(
                        customer_profile_id=rp.customer_profile_id,
                        status=True,
                        status_detail='active'
                        ).order_by('-update_dt')
    if not payment_profiles:
        valid_cpp_ids, invalid_cpp_ids = rp.populate_payment_profile()
        #print valid_cpp_ids, invalid_cpp_ids

        if valid_cpp_ids:
            payment_profiles = PaymentProfile.objects.filter(
                           customer_profile_id=valid_cpp_ids[0])

    if not payment_profiles:
        result_data['reason'] = 'not setup'
    else:
        if rp.status_detail == 'active':
            num_processed = run_a_recurring_payment(rp)
            if num_processed:
                result_data['processed'] = 'true'
                result_data['reason'] = 'processed'
                # get total_paid and balance for this rp
                result_data['total_paid'] = str(rp.total_paid)
                result_data['balance'] = str(rp.get_outstanding_balance())

                # get total amount received for all rps
                d = RecurringPaymentInvoice.objects.filter(
                                            invoice__balance=0,
                                            ).aggregate(total_amount_received=Sum('invoice__total'))
                result_data['total_amount_received'] = d['total_amount_received']
                if not result_data['total_amount_received']:
                    result_data['total_amount_received'] = 0
                result_data['total_amount_received'] = tcurrency(result_data['total_amount_received'])


    return HttpResponse(simplejson.dumps(result_data))


@staff_member_required
def customers(request, template_name="recurring_payments/customers.html"):
    """Display a list of recurring payment accounts.
    """
    query = request.GET.get('q', None)
    if get_setting('site', 'global', 'searchindex') and query:
        recurring_payments = RecurringPayment.objects.search(query)
    else:
        recurring_payments = RecurringPayment.objects.all()
    total_customers = RecurringPayment.objects.count()
    # get total amount received
    d = RecurringPaymentInvoice.objects.filter(
                                invoice__balance=0,
                                ).aggregate(total_amount_received=Sum('invoice__total'))
    total_amount_received = d['total_amount_received']
    if not total_amount_received:
        total_amount_received = 0
    # get total amount unpaid
    d = RecurringPaymentInvoice.objects.filter(
                                invoice__balance__gt=0,
                                ).aggregate(total_amount_unpaid=Sum('invoice__balance'))
    total_amount_unpaid = d['total_amount_unpaid']
    if not total_amount_unpaid:
        total_amount_unpaid = 0

    # get total amount past due
    d = RecurringPaymentInvoice.objects.filter(
                                invoice__balance__gt=0,
                                billing_dt__lte=datetime.now()
                                ).aggregate(total_amount_past_due=Sum('invoice__balance'))
    total_amount_past_due = d['total_amount_past_due']
    if not total_amount_past_due:
        total_amount_past_due = 0

    return render_to_response(template_name, {
                    'recurring_payments': recurring_payments,
                    'total_customers': total_customers,
                    'total_amount_received': total_amount_received,
                    'total_amount_unpaid': total_amount_unpaid,
                    'total_amount_past_due': total_amount_past_due,
                    'query': query
                                              },
        context_instance=RequestContext(request))


def transaction_receipt(request, rp_id, payment_transaction_id, rp_guid=None,
                        template_name="recurring_payments/transaction_receipt.html"):
    """Display a transaction receipt.
    """
    if request.user.is_authenticated():
        rp = get_object_or_404(RecurringPayment, pk=rp_id)
        # only admin or user self can access this page
        if not request.user.profile.is_superuser and request.user.id != rp.user.id:
            raise Http403
    else:
        if not rp_guid: raise Http403
        rp = get_object_or_404(RecurringPayment, pk=rp_id, guid=rp_guid)

    payment_transaction = get_object_or_404(PaymentTransaction,
                                            pk=payment_transaction_id,
                                            status=True)
    payment_profile = PaymentProfile.objects.filter(
                    payment_profile_id=payment_transaction.payment_profile_id)[0]
    invoice = payment_transaction.payment.invoice


    return render_to_response(template_name, {
                    'rp': rp,
                    'invoice': invoice,
                    'payment_transaction': payment_transaction,
                    'payment_profile': payment_profile
                                              },
        context_instance=RequestContext(request))


@login_required
def disable_account(request, rp_id,
                          template_name="recurring_payments/disable.html"):
    """Disable a recurring payment account.
    """
    rp = get_object_or_404(RecurringPayment, pk=rp_id)

    # only admin or user self can access this page
    if not request.user.profile.is_superuser and request.user.id != rp.user.id:
        raise Http403
    if request.method == "POST":
        if request.POST.get('cancel'):
            return HttpResponseRedirect(reverse('recurring_payment.view_account', args=[rp.id]))
        else:

            rp.status_detail = 'disabled'
            rp.save()

            log_description = '%s disabled' % rp._meta.object_name

            # delete the CIM account - only if there is no other rps sharing the same customer profile
            is_deleted = rp.delete_customer_profile()
            if is_deleted:
                log_description = "%s as well as its CIM account." % log_description

                rp.customer_profile_id = ''
                rp.save()



            # send an email to admin
            rp_email_notice = RecurringPaymentEmailNotices()
            rp_email_notice.email_admins_account_disabled(rp, request.user)


            # log an event
            EventLog.objects.log(instance=rp)

            messages.add_message(request, messages.SUCCESS, _('Successfully disabled %(rp)s' % {'rp': rp}))

            return HttpResponseRedirect(reverse('recurring_payment.view_account', args=[rp.id]))


    return render_to_response(template_name, {
                    'rp': rp},
        context_instance=RequestContext(request))
