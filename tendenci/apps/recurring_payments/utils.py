from __future__ import print_function
from datetime import datetime
import time
from decimal import Decimal
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from dateutil.relativedelta import relativedelta
from tendenci.apps.emails.models import Email
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.profiles.models import Profile
from tendenci.apps.recurring_payments.models import (RecurringPayment,
                                       PaymentProfile,
                                       RecurringPaymentInvoice,
                                       PaymentTransaction)
from tendenci.apps.recurring_payments.authnet.cim import CIMCustomerProfile, CIMHostedProfilePage
from tendenci.apps.recurring_payments.authnet.utils import get_token
from tendenci.apps.recurring_payments.authnet.utils import payment_update_from_response
from tendenci.apps.payments.models import Payment

UNSUCCESSFUL_TRANS_CODE = ['E00027']


class RecurringPaymentEmailNotices(object):
    def __init__(self):
        self.site_display_name = get_setting('site', 'global', 'sitedisplayname')
        self.site_contact_name = get_setting('site', 'global', 'sitecontactname')
        self.site_contact_email = get_setting('site', 'global', 'sitecontactemail')
        self.reply_to_email = get_setting('module', 'payments', 'paymentrecipients')
        if not self.reply_to_email:
            self.reply_to_email = self.site_contact_email
        self.site_url = get_setting('site', 'global', 'siteurl')

        self.email = Email()
        self.email.sender = get_setting('site', 'global', 'siteemailnoreplyaddress')
        self.email.sender_display = self.site_display_name
        self.email.reply_to = self.reply_to_email

        self.admin_emails = self.get_admin_emails()

    def get_admin_emails(self):
        payment_admins = get_setting('module', 'payments', 'paymentrecipients')
        if payment_admins:
            payment_admins = payment_admins.split(',')
            admin_emails = payment_admins
        else:
            admin_emails = (get_setting('site', 'global', 'admincontactemail')).split(',')

        if admin_emails:
            admin_emails = ','.join(admin_emails)

        return admin_emails

    def get_script_support_emails(self):
        admins = getattr(settings, 'ADMINS', None)
        if admins:
            recipients_list = [admin[1] for admin in admins]
            return ','.join(recipients_list)

        return None

    def email_script_support_transaction_error(self, payment_transaction):
        """if there is an error other than transaction not being approved, notify us.
        """
        self.email.recipient = self.get_script_support_emails()
        if self.email.recipient:
            template_name = "recurring_payments/email_script_support_transaction.html"
            try:
                email_content = render_to_string(template_name,
                                               {'pt':payment_transaction,
                                                'site_display_name': self.site_display_name,
                                                'site_url': self.site_url
                                                })
                self.email.body = email_content
                self.email.content_type = "html"
                self.email.priority = 1
                self.email.subject = _('Recurring payment transaction error on %(dname)s' % {
                                                                            'dname':self.site_display_name})

                self.email.send()
            except TemplateDoesNotExist:
                pass

    def email_admins_transaction_result(self, payment_transaction, success=True):
        """Send admins the result after the transaction is processed.
        """
        self.email.recipient = self.admin_emails
        if self.email.recipient:
            template_name = "recurring_payments/email_admins_transaction.html"
            user_in_texas = False
            if payment_transaction.payment.state:
                if payment_transaction.payment.state.lower() in ['texas', 'tx']:
                    user_in_texas = True
            try:
                email_content = render_to_string(template_name,
                                               {'pt':payment_transaction,
                                                'site_display_name': self.site_display_name,
                                                'site_url': self.site_url,
                                                'user_in_texas': user_in_texas
                                                })
                self.email.body = email_content
                self.email.content_type = "html"
                if not success:
                    self.email.subject = _('Recurring payment transaction failed on %(dname)s' % {
                                                                            'dname': self.site_display_name})
                    self.email.priority = 1
                else:
                    self.email.subject = _('Recurring payment transaction processed on %(dname)s' % {
                                                                                'dname': self.site_display_name})

                self.email.send()
            except TemplateDoesNotExist:
                pass

    def email_customer_transaction_result(self, payment_transaction):
        """Send customer an email after the transaction is processed.
        """
        self.email.recipient = payment_transaction.recurring_payment.user.email
        if self.email.recipient:
            template_name = "recurring_payments/email_customer_transaction.html"
            try:
                email_content = render_to_string(template_name,
                                               {'pt':payment_transaction,
                                                'site_display_name': self.site_display_name,
                                                'site_url': self.site_url
                                                })
                self.email.body = email_content
                self.email.content_type = "html"
                if payment_transaction.status:
                    self.email.subject = _('Payment received ')
                else:
                    self.email.subject = _('Payment failed ')
                self.email.subject = _("%(subj)s for %(desc)s " % {
                            'subj': self.email.subject,
                            'desc': payment_transaction.recurring_payment.description})

                self.email.send()
            except TemplateDoesNotExist:
                pass

    def email_admins_no_payment_profile(self, recurring_payment):
        """Notify admin that payment method hasn't been setup yet for this recurring payment entry.
        """
        self.email.recipient = self.admin_emails
        if self.email.recipient:
            template_name = "recurring_payments/email_admins_no_payment_profile.html"
            try:
                email_content = render_to_string(template_name,
                                               {'rp':recurring_payment,
                                                'site_display_name': self.site_display_name,
                                                'site_url': self.site_url
                                                })
                self.email.body = email_content
                self.email.content_type = "html"
                self.email.subject = _('Payment method not setup for %(rp)s on %(dname)s' % {
                                    'rp': recurring_payment ,
                                    'dname': self.site_display_name})

                self.email.send()
            except TemplateDoesNotExist:
                pass

    def email_customer_no_payment_profile(self, recurring_payment):
        """Notify customer that payment method hasn't been setup yet for this recurring payment entry.
        """
        self.email.recipient = recurring_payment.user.email
        if self.email.recipient:
            template_name = "recurring_payments/email_customer_no_payment_profile.html"
            try:
                email_content = render_to_string(template_name,
                                               {'rp':recurring_payment,
                                                'site_display_name': self.site_display_name,
                                                'site_url': self.site_url
                                                })
                self.email.body = email_content
                self.email.content_type = "html"
                self.email.subject = _('Please update your payment method for %(rp)s on %(dname)s' % {
                                    'rp': recurring_payment.description,
                                    'dname': self.site_display_name})

                self.email.send()
            except TemplateDoesNotExist:
                pass

    def email_admins_account_disabled(self, recurring_payment, user_by):
        """Notify admin that the recurring payment account is disabled.
        """
        self.email.recipient = self.admin_emails
        if self.email.recipient:
            template_name = "recurring_payments/email_admins_account_disabled.html"
            try:
                email_content = render_to_string(template_name,
                                               {'rp':recurring_payment,
                                                'user_by': user_by,
                                                'site_display_name': self.site_display_name,
                                                'site_url': self.site_url
                                                })
                self.email.body = email_content
                self.email.content_type = "html"
                self.email.subject = _('Recurring Payment Account (ID:%(id)d) Disabled by %(usr)s on %(dname)s' % {
                       'id':recurring_payment.id,
                       'usr' : user_by,
                       'dname': self.site_display_name})

                self.email.send()
            except TemplateDoesNotExist:
                pass


def run_a_recurring_payment(rp, verbosity=0):
    """
        1) check and populate payment profile for each recurring payment entry.
        2) generate invoice(s) for recurring payments if needed.
        3) make payment transactions for invoice(s) upon due date.
        4) notify admins and customers for after each transaction.
    """
    num_processed = 0
    if rp.status_detail == 'active':
        rp_email_notice = RecurringPaymentEmailNotices()
        now = datetime.now()
        currency_symbol = get_setting('site', 'global', 'currencysymbol')

        # check and store payment profiles in local db
        if verbosity > 1:
            print()
            print('Processing for "%s":' % rp)
            print('...Populating payment profiles from payment gateway...')
        rp.populate_payment_profile()

        # create invoices if needed
        if verbosity > 1:
            print('...Checking and generating invoice(s)  ...')
        rp.check_and_generate_invoices()

        # look for unpaid invoices with current due date or pass due date
        rp_invoices = RecurringPaymentInvoice.objects.filter(
                                             recurring_payment=rp,
                                             invoice__balance__gt=0,
                                             billing_dt__lte=now
                                             ).order_by('billing_cycle_start_dt')

        if rp_invoices:
            payment_profiles = PaymentProfile.objects.filter(
                        customer_profile_id=rp.customer_profile_id,
                        status=True,
                        status_detail='active'
                        ).order_by('-update_dt')

            if payment_profiles:

                for i, rp_invoice in enumerate(rp_invoices):
                    # wait for 3 minutes (duplicate transaction window is 2 minutes) if this is not the first invoice,
                    # otherwise, the payment gateway would through the "duplicate transaction" error.
                    if i > 0: time.sleep(3*60)

                    payment_profile = payment_profiles[0]
                    if rp_invoice.last_payment_failed_dt and \
                        rp_invoice.last_payment_failed_dt > payment_profile.update_dt:
                        # this invoice was processed but failed, and they haven't update the payment profile yet,
                        # so just skip it for now.
                        # only skip if the error code is: E00027 - the transaction was unsuccessful
                        last_error_code = rp_invoice.get_last_transaction_error_code()
                        if last_error_code and last_error_code in UNSUCCESSFUL_TRANS_CODE:
                            continue

                    # make payment transaction and then update recurring_payment fields
                    if verbosity > 1:
                        print('...Making payment transaction for billing cycle (%s -%s) - amount: %s%.2f ...' \
                                % (rp_invoice.billing_cycle_start_dt.strftime('%m-%d-%Y'),
                                   rp_invoice.billing_cycle_end_dt.strftime('%m-%d-%Y'),
                                   currency_symbol,
                                   rp_invoice.invoice.balance))

                    success = False

                    payment_profile_id = payment_profile.payment_profile_id
                    payment_transaction = rp_invoice.make_payment_transaction(payment_profile_id)
                    if payment_transaction.status:
                        success = True
                        num_processed += 1


                    if success:
                        rp.last_payment_received_dt = now
                        rp_invoice.payment_received_dt = now
                        rp_invoice.save()
                        rp.num_billing_cycle_completed += 1
                        print('...Success.')
                    else:
                        rp.num_billing_cycle_failed += 1
                        print('...Failed  - \n\t code - %s \n\t text - %s' \
                                            % (payment_transaction.message_code,
                                               payment_transaction.message_text))

                    # send out email notifications - for both successful and failed transactions
                    # to admin
                    rp_email_notice.email_admins_transaction_result(payment_transaction, success=success)
                    # to customer
                    if payment_transaction.message_code not in UNSUCCESSFUL_TRANS_CODE:
                        rp_email_notice.email_customer_transaction_result(payment_transaction)
                    else:
                        # the payment gateway is probably not configured correctly
                        # email to tendenci script support
                        rp_email_notice.email_script_support_transaction_error(payment_transaction)
            else:
                # email admin - payment profile not set up
                # to admin
                rp_email_notice.email_admins_no_payment_profile(rp)
                # to customer
                rp_email_notice.email_customer_no_payment_profile(rp)


        # calculate the balance by checking for unpaid invoices
        rp.balance = rp.get_current_balance()
        rp.outstanding_balance = rp.get_outstanding_balance()
        rp.save()

    return num_processed


def api_rp_setup(data):
    """Create a recurrring payment account. Accepted format: json

    Input fields:
        email - required
        description - required
        amount - required
        cp_id - customer profile id, required
        pp_id - customer payment profile id, required
        billing_cycle_start_dt - required
        billing_cycle_end_dt - required
        response_str - required
        login_name
        login_password
        url
        first_name
        last_name


        billing_period - optional, default to 'month'
        billing_frequency - optional, default to 1
        billing_start_dt - optional, default to today
        num_days - optional, default to 0
        has_trial_period - optional, default to False
        trial_period_start_dt - optional, default to today
        trial_period_end_dt - optional, default to today
        trial_amount - optional, default to 0

    Output:
        rp_id - a recurring payment id
        rp_url - url to rp
        username
        result_code
    """
    from decimal import Decimal
    from tendenci.apps.base.utils import validate_email
    import dateutil.parser as dparser
    from tendenci.apps.imports.utils import get_unique_username

    email = data.get('email', '')
    description = data.get('description', '')
    url = data.get('url')
    payment_amount = data.get('amount', '')
    taxable = data.get('taxable', 0)
    if taxable in ('True', 'true', '1', 1):
        taxable = 1
    else:
        taxable = 0
    try:
        tax_rate = Decimal(data.get('tax_rate', 0))
        if tax_rate > 1: tax_rate = 0
    except:
        tax_rate = 0
    tax_exempt = data.get('tax_exempt', 0)
    if tax_exempt in ('True', 'true', '1', 1):
        tax_exempt = 1
    else:
        tax_exempt = 0
    try:
        payment_amount = Decimal(payment_amount)
    except:
        payment_amount = 0
    cp_id = data.get('cp_id')
    pp_id = data.get('pp_id')
    billing_cycle_start_dt = data.get('billing_cycle_start_dt')
    if billing_cycle_start_dt:
        billing_cycle_start_dt = dparser.parse(billing_cycle_start_dt)
    billing_cycle_end_dt = data.get('billing_cycle_end_dt')
    if billing_cycle_end_dt:
        billing_cycle_end_dt = dparser.parse(billing_cycle_end_dt)

    direct_response_str = data.get('response_str')

    if not all([validate_email(email),
                description,
                payment_amount>0,
                cp_id,
                pp_id,
                billing_cycle_start_dt,
                billing_cycle_end_dt,
                direct_response_str]
               ):
        return False, {}

    # 1) get or create user
    username = data.get('login_name')

    # check if user already exists based on email and username
    users = User.objects.filter(email=email, username=username)
    if users:
        u = users[0]
    else:
        # create user account
        u = User()
        u.email=email
        u.username = username
        if not u.username:
            u.username = email.split('@')[0]
        u.username = get_unique_username(u)
        raw_password = data.get('login_password')
        if not raw_password:
            raw_password = User.objects.make_random_password(length=8)
        u.set_password(raw_password)
        u.first_name = data.get('first_name', '')
        u.last_name = data.get('last_name', '')
        u.is_staff = False
        u.is_superuser = False
        u.save()

        profile = Profile.objects.create(
           user=u,
           creator=u,
           creator_username=u.username,
           owner=u,
           owner_username=u.username,
           email=u.email
        )

    # 2) create a recurring payment account
    rp = RecurringPayment()
    rp.user = u
    rp.description = description
    rp.url = url
    rp.payment_amount = payment_amount
    rp.taxable = taxable
    rp.tax_rate = tax_rate
    rp.tax_exempt = tax_exempt
    rp.customer_profile_id = cp_id
    rp.billing_start_dt = billing_cycle_start_dt

    has_trial_period = data.get('has_trial_period')
    trial_period_start_dt = data.get('trial_period_start_dt')
    trial_period_end_dt = data.get('trial_period_end_dt')
    if has_trial_period in ['True', '1',  True, 1] and all([trial_period_start_dt,
                                                            trial_period_end_dt]):
        rp.has_trial_period = True
        rp.trial_period_start_dt = dparser.parse(trial_period_start_dt)
        rp.trial_period_end_dt = dparser.parse(trial_period_end_dt)
    else:
        rp.has_trial_period = False

    rp.status_detail = 'active'
    rp.save()

    # 3) create a payment profile account
    payment_profile_exists = PaymentProfile.objects.filter(
                                        customer_profile_id=cp_id,
                                        payment_profile_id=pp_id
                                        ).exists()
    if not payment_profile_exists:
        PaymentProfile.objects.create(
                        customer_profile_id=cp_id,
                        payment_profile_id=pp_id,
                        owner=u,
                        owner_username=u.username
                        )

    # 4) create rp invoice
    billing_cycle = {'start': billing_cycle_start_dt,
                     'end': billing_cycle_end_dt}
    rp_invoice = rp.create_invoice(billing_cycle, billing_cycle_start_dt)
    rp_invoice.invoice.tender(rp.user)

    # 5) create rp transaction
    now = datetime.now()
    payment = Payment()
    payment.payments_pop_by_invoice_user(rp.user,
                                         rp_invoice.invoice,
                                         rp_invoice.invoice.guid)
    payment_transaction = PaymentTransaction(
                                    recurring_payment=rp,
                                    recurring_payment_invoice=rp_invoice,
                                    payment_profile_id=pp_id,
                                    trans_type='auth_capture',
                                    amount=rp_invoice.invoice.total,
                                    status=True)
    payment = payment_update_from_response(payment, direct_response_str)
    payment.mark_as_paid()
    payment.save()
    rp_invoice.invoice.make_payment(rp.user, Decimal(payment.amount))
    rp_invoice.invoice.save()


    rp_invoice.payment_received_dt = now
    rp_invoice.save()
    rp.last_payment_received_dt = now
    rp.num_billing_cycle_completed += 1
    rp.save()

    payment_transaction.payment = payment
    payment_transaction.result_code = data.get('result_code')
    payment_transaction.message_code = data.get('message_code')
    payment_transaction.message_text = data.get('message_text')

    payment_transaction.save()

    site_url = get_setting('site', 'global', 'siteurl')


    return True, {'rp_id': rp.id,
                  'rp_url': '%s%s' %  (site_url,
                                reverse('recurring_payment.view_account', args=[rp.id])),
                  'username': rp.user.username}

def api_add_rp(data):
    """Create a recurrring payment account. Accepted format: json

    Input fields:
        email - required
        description - required
        payment_amount - required
        billing_period - optional, default to 'month'
        billing_frequency - optional, default to 1
        billing_start_dt - optional, default to today
        num_days - optional, default to 0
        has_trial_period - optional, default to False
        trial_period_start_dt - optional, default to today
        trial_period_end_dt - optional, default to today
        trial_amount - optional, default to 0

    Output:
        rp_id - a recurring payment id
        result_code
    """
    ALLOWED_FIELES = ('email',
                      'description',
                      'payment_amount',
                      'billing_period',
                      'billing_frequency',
                      'billing_start_dt',
                      'num_days',
                      'has_trial_period',
                      'trial_period_start_dt',
                      'trial_period_end_dt',
                      'trial_amount',
                      )
    from decimal import Decimal
    from tendenci.apps.base.utils import validate_email
    import dateutil.parser as dparser
    from tendenci.apps.imports.utils import get_unique_username

    email = data.get('email', '')
    payment_amount = data.get('payment_amount', '')
    try:
        payment_amount = Decimal(payment_amount)
    except:
        payment_amount = 0


    if not all([validate_email(email),
                'description' in data,
                payment_amount>0]):
        return False, {}


    rp = RecurringPayment()
    for key, value in data.items():
        if key in ALLOWED_FIELES:
            if hasattr(rp, key):
                setattr(rp, key, value)

    if rp.billing_start_dt:
        try:
            rp.billing_start_dt = dparser.parse(rp.billing_start_dt)
        except:
            rp.billing_start_dt = datetime.now()
    else:
        rp.billing_start_dt = datetime.now()
    if rp.trial_period_start_dt:
        try:
            rp.trial_period_start_dt = dparser.parse(rp.trial_period_start_dt)
        except:
            rp.trial_period_start_dt = datetime.now()

    if rp.trial_period_end_dt:
        try:
            rp.trial_period_end_dt = dparser.parse(rp.trial_period_end_dt)
        except:
            rp.trial_period_end_dt = datetime.now()

    rp.payment_amount = Decimal(rp.payment_amount)

    try:
        rp.billing_frequency = int(rp.billing_frequency)
    except:
        rp.billing_frequency = 1
    try:
        rp.num_days = int(rp.num_days)
    except:
        rp.num_days = 1
    if rp.has_trial_period in ['True', '1',  True, 1] and all([rp.trial_period_start_dt,
                                                              rp.trial_period_end_dt]):
        rp.has_trial_period = True
    else:
        rp.has_trial_period = False

    # start the real work

#    # get or create a user account with this email
#    users = User.objects.filter(email=email)
#    if users:
#        u = users[0]
#    else:

    # always create a new user account - This is very important!
    # it is to prevent hacker from trying to use somebody else's account.
    u = User()
    u.email=email
    u.username = data.get('username', '')
    if not u.username:
        u.username = email.split('@')[0]
    u.username = get_unique_username(u)
    raw_password = data.get('password', '')
    if not raw_password:
        raw_password = User.objects.make_random_password(length=8)
    u.set_password(raw_password)
    u.first_name = data.get('first_name', '')
    u.last_name = data.get('last_name', '')
    u.is_staff = False
    u.is_superuser = False
    u.save()

#    profile = Profile.objects.create(
#           user=u,
#           creator=u,
#           creator_username=u.username,
#           owner=u,
#           owner_username=u.username,
#           email=u.email
#        )

    # add a recurring payment entry for this user
    rp.user = u
    # activate it when payment info is received
    rp.status_detail = 'inactive'
    rp.save()

    return True, {'rp_id': rp.id}


def api_get_rp_token(data):
    """Get the token for using authorize.net hosted profile page
        Accepted format: json

    Input fields:
        rp_id - required
        iframe_communicator_url

    Output:
        token
        gateway_error
        payment_profile_id
        result_code
    """
    rp_id = data.get('rp_id', 0)
    iframe_communicator_url = data.get('iframe_communicator_url', '')

    try:
        rp = RecurringPayment.objects.get(id=int(rp_id))
    except:
        return False, {}

    token, gateway_error = get_token(rp, CIMCustomerProfile,
                                     CIMHostedProfilePage,
                                     iframe_communicator_url)

    d = {'token': token,
         'gateway_error': gateway_error}

    # also pass the payment_profile_id
    payment_profiles = PaymentProfile.objects.filter(customer_profile_id=rp.customer_profile_id,
                                                    status=True,
                                                    status_detail='active')
    if payment_profiles:
        payment_profile_id = (payment_profiles[0]).payment_profile_id
    else:
        payment_profile_id = ''

    d['payment_profile_id'] = payment_profile_id


    if gateway_error:
        status = False
    else:
        status = True

    return status, d


def api_verify_rp_payment_profile(data):
    """Verify if this recurring payment account
        has a valid payment profile.
        Accepted format: json

    Input fields:
        rp_id - required

    Output:
        has_payment_profile
        result_code
    """
    rp_id = data.get('rp_id', 0)

    try:
        rp = RecurringPayment.objects.get(id=int(rp_id))
    except:
        return False, {}

    d = {}
    pay_now = data.get('pay_now', '')
    if pay_now == 'yes': pay_now = True
    else: pay_now = False

    # pp - customer payment_profile
    validation_mode=''
    if not pay_now:
        validation_mode='liveMode'

    is_valid = True

    valid_cpp_ids, invalid_cpp_ids = rp.populate_payment_profile(validation_mode=validation_mode)
    if valid_cpp_ids:
        d['valid_cpp_id'] = valid_cpp_ids[0]

        if pay_now:
            # make a transaction NOW
            billing_cycle = {'start': rp.billing_start_dt,
                             'end': rp.billing_start_dt + relativedelta(months=rp.billing_frequency)}
            billing_dt = datetime.now()
            rp_invoice = rp.create_invoice(billing_cycle, billing_dt)
            payment_transaction = rp_invoice.make_payment_transaction(d['valid_cpp_id'])
            if not payment_transaction.status:
                # payment failed
                rp.num_billing_cycle_failed += 1
                rp.save()
                d['invalid_cpp_id'] = d['valid_cpp_id']
                d['valid_cpp_id'] = ''
                is_valid = False
            else:
                # success

                # update rp and rp_invoice
                if rp.status_detail != 'active':
                    rp.status_detail = 'active'

                now = datetime.now()
                rp.last_payment_received_dt = now
                rp.num_billing_cycle_completed += 1
                rp.save()
                rp_invoice.payment_received_dt = now
                rp_invoice.save()


                # send out the invoice view page
                d['receipt_url'] = '%s%s' % (get_setting('site', 'global', 'siteurl'),
                                             reverse('recurring_payment.transaction_receipt',
                                                args=[rp.id,
                                                payment_transaction.id,
                                                rp.guid]))

                # email to user
                rp_email_notice = RecurringPaymentEmailNotices()
                rp_email_notice.email_customer_transaction_result(payment_transaction)



    if invalid_cpp_ids:
        d['invalid_cpp_id']= invalid_cpp_ids[0]

    return is_valid, d
