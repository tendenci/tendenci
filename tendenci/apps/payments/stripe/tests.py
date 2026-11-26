from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from tendenci.apps.invoices.models import Invoice
from tendenci.apps.payments.models import Payment
from tendenci.apps.payments.stripe.utils import (
    build_payment_intent_params,
    charge_customer_off_session,
    payment_method_code_from_intent,
    payment_update_from_intent,
    user_facing_stripe_message,
)
from tendenci.apps.payments.stripe.views import _create_payment_intent_for_payment

# Host the browser is on, deliberately different from the Site URL setting.
BROWSED_HOST = 'payments.example.com'


def _make_invoice(**kwargs):
    defaults = {
        'title': 'Stripe test invoice',
        'due_date': timezone.now(),
        'status_detail': 'tendered',
        'tender_date': timezone.now(),
        'balance': Decimal('10.00'),
        'total': Decimal('10.00'),
        'subtotal': Decimal('10.00'),
        'payments_credits': Decimal('0.00'),
    }
    defaults.update(kwargs)
    return baker.make(Invoice, **defaults)


def _make_payment(invoice=None, **kwargs):
    invoice = invoice or _make_invoice()
    defaults = {
        'invoice': invoice,
        'amount': Decimal('10.00'),
        'description': 'Stripe test payment',
        'response_code': '',
        'response_reason_code': '',
        'status_detail': '',
        'zip': '12345',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'payment_intent_id': 'pi_stored',
    }
    defaults.update(kwargs)
    return baker.make(Payment, **defaults)


class BuildPaymentIntentParamsTests(TestCase):
    def test_basic_params_include_amount_metadata_and_no_method_types(self):
        payment = MagicMock()
        payment.id = 6
        payment.guid = 'guid-6'
        payment.amount = Decimal('10.50')
        payment.description = 'Membership'
        payment.invoice.stripe_connected_account.return_value = (None, None)

        params = build_payment_intent_params(payment, 'eur')

        self.assertEqual(params['amount'], 1050)
        self.assertEqual(params['currency'], 'eur')
        self.assertEqual(params['description'], 'Membership')
        self.assertEqual(params['metadata']['tendenci_payment_id'], '6')
        self.assertEqual(params['metadata']['tendenci_payment_guid'], 'guid-6')
        self.assertNotIn('payment_method_types', params)
        self.assertNotIn('customer', params)
        self.assertNotIn('setup_future_usage', params)

    def test_customer_and_setup_future_usage(self):
        payment = MagicMock()
        payment.id = 1
        payment.guid = 'g'
        payment.amount = Decimal('1.00')
        payment.description = 'd'
        payment.invoice.stripe_connected_account.return_value = (None, None)

        params = build_payment_intent_params(
            payment, 'usd',
            customer_id='cus_123',
            setup_future_usage='off_session',
        )

        self.assertEqual(params['customer'], 'cus_123')
        self.assertEqual(params['setup_future_usage'], 'off_session')

    @patch('tendenci.apps.payments.stripe.utils.get_setting')
    def test_express_connect_adds_fee_and_transfer_data(self, mock_get_setting):
        mock_get_setting.return_value = 'ca_test_client'
        payment = MagicMock()
        payment.id = 1
        payment.guid = 'g'
        payment.amount = Decimal('100.00')
        payment.description = 'd'
        payment.invoice.stripe_connected_account.return_value = (
            'acct_express', 'express')
        payment.invoice.get_stripe_application_fee.return_value = Decimal('3.20')

        params = build_payment_intent_params(payment, 'usd')

        self.assertEqual(params['application_fee_amount'], 320)
        self.assertEqual(
            params['transfer_data'], {'destination': 'acct_express'})
        self.assertNotIn('stripe_account', params)

    @patch('tendenci.apps.payments.stripe.utils.get_setting')
    def test_standard_connect_sets_stripe_account(self, mock_get_setting):
        mock_get_setting.return_value = 'ca_test_client'
        payment = MagicMock()
        payment.id = 1
        payment.guid = 'g'
        payment.amount = Decimal('100.00')
        payment.description = 'd'
        payment.invoice.stripe_connected_account.return_value = (
            'acct_standard', 'standard')

        params = build_payment_intent_params(payment, 'usd')

        self.assertEqual(params['stripe_account'], 'acct_standard')
        self.assertNotIn('transfer_data', params)
        self.assertNotIn('application_fee_amount', params)


class PaymentUpdateFromIntentTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = AnonymousUser()
        self.payment = _make_payment()

    def test_succeeded_stores_charge_id_and_approves(self):
        with patch.object(
                self.payment.invoice, 'make_payment', return_value=True) as mock_pay:
            intent = SimpleNamespace(
                status='succeeded',
                created=1234567890,
                latest_charge='ch_test_charge',
            )
            payment_update_from_intent(self.request, intent, self.payment)

        self.payment.refresh_from_db()
        self.assertTrue(self.payment.is_approved)
        self.assertEqual(self.payment.trans_id, 'ch_test_charge')
        self.assertEqual(self.payment.status_detail, 'approved')
        mock_pay.assert_called_once()

    def test_non_succeeded_does_not_approve(self):
        intent = SimpleNamespace(
            status='requires_payment_method',
            created=1,
            latest_charge=None,
        )
        payment_update_from_intent(self.request, intent, self.payment)

        self.payment.refresh_from_db()
        self.assertFalse(self.payment.is_approved)
        self.assertIn('requires_payment_method', self.payment.response_reason_text)
        self.assertEqual(self.payment.trans_id, '')

    def test_apple_pay_charge_replaces_cc(self):
        self.payment.method = 'cc'
        self.payment.save(update_fields=['method'])
        intent = SimpleNamespace(
            status='succeeded',
            created=1,
            latest_charge=SimpleNamespace(
                id='ch_apple',
                payment_method_details=SimpleNamespace(
                    type='card',
                    card=SimpleNamespace(
                        wallet=SimpleNamespace(type='apple_pay')),
                ),
            ),
        )
        with patch.object(
                self.payment.invoice, 'make_payment', return_value=True):
            payment_update_from_intent(self.request, intent, self.payment)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.method, 'applepay')
        self.assertEqual(self.payment.trans_id, 'ch_apple')


class ChargeCustomerOffSessionTests(TestCase):
    @patch('tendenci.apps.payments.stripe.utils.get_setting', return_value='usd')
    @patch('tendenci.apps.payments.stripe.utils.configure_stripe')
    @patch('tendenci.apps.payments.stripe.utils.customer_off_session_payment_method_id',
           return_value='pm_card')
    def test_success_returns_charge_id(
            self, mock_pm, mock_configure, mock_currency):
        payment = MagicMock()
        payment.id = 9
        payment.guid = 'guid-9'
        payment.amount = Decimal('25.00')
        payment.description = 'RP'
        payment.invoice.stripe_connected_account.return_value = (None, None)

        stripe_module = MagicMock()
        stripe_module.PaymentIntent.create.return_value = SimpleNamespace(
            status='succeeded',
            created=42,
            latest_charge='ch_off_session',
        )

        ok, response = charge_customer_off_session(
            stripe_module, payment, 'cus_1', description='Renewal',
            idempotency_key='tendenci-rp-invoice-3-2500')

        self.assertTrue(ok)
        self.assertEqual(response['status_detail'], 'approved')
        self.assertEqual(response['trans_id'], 'ch_off_session')
        create_kwargs = stripe_module.PaymentIntent.create.call_args.kwargs
        self.assertTrue(create_kwargs['confirm'])
        self.assertTrue(create_kwargs['off_session'])
        self.assertEqual(create_kwargs['payment_method'], 'pm_card')
        self.assertEqual(
            create_kwargs['idempotency_key'], 'tendenci-rp-invoice-3-2500')
        self.assertEqual(create_kwargs['expand'], ['latest_charge'])
        self.assertNotIn('payment_method_types', create_kwargs)
        self.assertNotIn('method', response)

    @patch('tendenci.apps.payments.stripe.utils.get_setting', return_value='usd')
    @patch('tendenci.apps.payments.stripe.utils.configure_stripe')
    @patch('tendenci.apps.payments.stripe.utils.customer_off_session_payment_method_id',
           return_value='pm_payto')
    def test_payto_charge_is_recorded(
            self, mock_pm, mock_configure, mock_currency):
        payment = MagicMock()
        payment.id = 9
        payment.guid = 'guid-9'
        payment.amount = Decimal('25.00')
        payment.description = 'RP'
        payment.invoice.stripe_connected_account.return_value = (None, None)
        stripe_module = MagicMock()
        stripe_module.PaymentIntent.create.return_value = SimpleNamespace(
            status='succeeded',
            created=42,
            latest_charge=SimpleNamespace(
                id='ch_payto',
                payment_method_details=SimpleNamespace(type='payto'),
            ),
        )

        ok, response = charge_customer_off_session(
            stripe_module, payment, 'cus_1')

        self.assertTrue(ok)
        self.assertEqual(response['method'], 'payto')
        self.assertEqual(response['trans_id'], 'ch_payto')

    @patch('tendenci.apps.payments.stripe.utils.get_setting', return_value='usd')
    @patch('tendenci.apps.payments.stripe.utils.configure_stripe')
    @patch('tendenci.apps.payments.stripe.utils.customer_off_session_payment_method_id',
           return_value='pm_card')
    def test_no_idempotency_key_when_not_supplied(
            self, mock_pm, mock_configure, mock_currency):
        payment = MagicMock()
        payment.id = 9
        payment.guid = 'guid-9'
        payment.amount = Decimal('25.00')
        payment.description = 'RP'
        payment.invoice.stripe_connected_account.return_value = (None, None)

        stripe_module = MagicMock()
        stripe_module.PaymentIntent.create.return_value = SimpleNamespace(
            status='succeeded', created=42, latest_charge='ch_x')

        charge_customer_off_session(stripe_module, payment, 'cus_1')

        self.assertNotIn(
            'idempotency_key',
            stripe_module.PaymentIntent.create.call_args.kwargs)

    @patch('tendenci.apps.payments.stripe.utils.get_setting', return_value='usd')
    @patch('tendenci.apps.payments.stripe.utils.configure_stripe')
    @patch('tendenci.apps.payments.stripe.utils.customer_off_session_payment_method_id',
           return_value='pm_card')
    def test_standard_connect_looks_up_method_on_connected_account(
            self, mock_pm, mock_configure, mock_currency):
        payment = MagicMock()
        payment.id = 9
        payment.guid = 'guid-9'
        payment.amount = Decimal('25.00')
        payment.description = 'RP'
        payment.invoice.stripe_connected_account.return_value = (
            'acct_standard', 'standard')

        stripe_module = MagicMock()
        stripe_module.PaymentIntent.create.return_value = SimpleNamespace(
            status='succeeded', created=42, latest_charge='ch_x')

        charge_customer_off_session(stripe_module, payment, 'cus_1')

        self.assertEqual(
            mock_pm.call_args.kwargs['request_options'],
            {'stripe_account': 'acct_standard'},
        )

    @patch('tendenci.apps.payments.stripe.utils.get_setting', return_value='usd')
    @patch('tendenci.apps.payments.stripe.utils.configure_stripe')
    @patch('tendenci.apps.payments.stripe.utils.customer_off_session_payment_method_id',
           return_value='')
    def test_missing_payment_method_fails(
            self, mock_pm, mock_configure, mock_currency):
        payment = MagicMock()
        payment.amount = Decimal('1.00')
        payment.description = 'x'
        payment.id = 1
        payment.guid = 'g'
        payment.invoice.stripe_connected_account.return_value = (None, None)

        ok, response = charge_customer_off_session(
            MagicMock(), payment, 'cus_1')

        self.assertFalse(ok)
        self.assertIn('No payment method', response['response_reason_text'])


@patch('tendenci.apps.payments.stripe.views.build_payment_intent_params',
       return_value={'amount': 1000, 'currency': 'usd'})
@patch('tendenci.apps.payments.stripe.views.configure_stripe')
@patch('tendenci.apps.payments.stripe.views._membership_for_auto_renew')
class CreatePaymentIntentTests(TestCase):
    """The auto-renew customer must live on the account that takes the charge."""

    def _payment_for(self, connected_account, scope):
        payment = MagicMock()
        payment.invoice.stripe_connected_account.return_value = (
            connected_account, scope)
        return payment

    def _create(self, payment):
        with patch('tendenci.apps.payments.stripe.views.stripe.Customer.create') as customer, \
                patch('tendenci.apps.payments.stripe.views.stripe.PaymentIntent.create'):
            customer.return_value = SimpleNamespace(id='cus_new')
            _create_payment_intent_for_payment(payment, 'usd')
        return customer

    def test_customer_created_on_standard_connected_account(
            self, mock_membership, mock_configure, mock_params):
        mock_membership.return_value = SimpleNamespace(
            user=SimpleNamespace(email='member@example.com'))

        customer = self._create(self._payment_for('acct_standard', 'standard'))

        self.assertEqual(
            customer.call_args.kwargs['stripe_account'], 'acct_standard')

    def test_customer_created_on_platform_for_express(
            self, mock_membership, mock_configure, mock_params):
        mock_membership.return_value = SimpleNamespace(
            user=SimpleNamespace(email='member@example.com'))

        customer = self._create(self._payment_for('acct_express', 'express'))

        self.assertNotIn('stripe_account', customer.call_args.kwargs)


@override_settings(
    STRIPE_SECRET_KEY='sk_test_dummy',
    STRIPE_PUBLISHABLE_KEY='pk_test_dummy',
)
class PayOnlineViewTests(TestCase):
    def setUp(self):
        self.payment = _make_payment()

    @patch('tendenci.apps.payments.stripe.views.render_to_resp')
    @patch('tendenci.apps.payments.stripe.views._create_payment_intent_for_payment')
    def test_pay_online_uses_request_host_for_finalize_url(
            self, mock_create_pi, mock_render):
        mock_create_pi.return_value = (
            SimpleNamespace(id='pi_created', client_secret='pi_secret_xyz'),
            None,
            None,
        )
        mock_render.return_value = HttpResponse('ok')

        with override_settings(ALLOWED_HOSTS=[BROWSED_HOST]):
            response = self.client.get(
                reverse('stripe.payonline',
                        args=[self.payment.id, self.payment.guid]),
                HTTP_HOST=BROWSED_HOST,
            )

        self.assertEqual(response.status_code, 200)
        context = mock_render.call_args.kwargs['context']
        self.assertEqual(context['client_secret'], 'pi_secret_xyz')
        self.assertTrue(
            context['finalize_url'].startswith(
                'http://%s/payments/stripe/payonline/' % BROWSED_HOST))
        self.assertIn('/finalize/', context['finalize_url'])

    @patch('tendenci.apps.payments.stripe.views.render_to_resp')
    @patch('tendenci.apps.payments.stripe.views._create_payment_intent_for_payment')
    def test_pay_online_stores_intent_id_and_connected_account(
            self, mock_create_pi, mock_render):
        mock_create_pi.return_value = (
            SimpleNamespace(id='pi_created', client_secret='pi_secret_xyz'),
            None,
            None,
        )
        mock_render.return_value = HttpResponse('ok')

        with patch.object(Invoice, 'stripe_connected_account',
                          return_value=('acct_standard', 'standard')):
            self.client.get(
                reverse('stripe.payonline',
                        args=[self.payment.id, self.payment.guid]))

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.payment_intent_id, 'pi_created')
        context = mock_render.call_args.kwargs['context']
        self.assertEqual(context['connected_account_id'], 'acct_standard')

    @patch('tendenci.apps.payments.stripe.views.render_to_resp')
    @patch('tendenci.apps.payments.stripe.views._create_payment_intent_for_payment')
    def test_pay_online_omits_connected_account_for_express(
            self, mock_create_pi, mock_render):
        mock_create_pi.return_value = (
            SimpleNamespace(id='pi_created', client_secret='pi_secret_xyz'),
            None,
            None,
        )
        mock_render.return_value = HttpResponse('ok')

        with patch.object(Invoice, 'stripe_connected_account',
                          return_value=('acct_express', 'express')):
            self.client.get(
                reverse('stripe.payonline',
                        args=[self.payment.id, self.payment.guid]))

        context = mock_render.call_args.kwargs['context']
        self.assertEqual(context['connected_account_id'], '')

    def test_pay_online_redirects_when_already_approved(self):
        self.payment.response_code = '1'
        self.payment.response_reason_code = '1'
        self.payment.status_detail = 'approved'
        self.payment.save()

        response = self.client.get(
            reverse('stripe.payonline', args=[self.payment.id, self.payment.guid]))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/thankyou/', response['Location'])

    @override_settings(STRIPE_SECRET_KEY='')
    def test_pay_online_redirects_when_stripe_not_configured(self):
        response = self.client.get(
            reverse('stripe.payonline', args=[self.payment.id, self.payment.guid]))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/invoices/', response['Location'])


@override_settings(STRIPE_SECRET_KEY='sk_test_dummy')
class SaveBillingViewTests(TestCase):
    def setUp(self):
        self.payment = _make_payment()
        self.url = reverse(
            'stripe.save_billing', args=[self.payment.id, self.payment.guid])

    def test_save_billing_ok(self):
        response = self.client.post(self.url, {
            'first_name': 'Ada',
            'last_name': 'Lovelace',
            'email': 'ada@example.com',
            'zip': '12345',
        })

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'ok': True})
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.first_name, 'Ada')
        self.assertEqual(self.payment.zip, '12345')

    def test_save_billing_requires_zip(self):
        response = self.client.post(self.url, {
            'first_name': 'Ada',
            'zip': '',
        })

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertFalse(payload['ok'])
        self.assertIn('zip', payload['errors'])

    def test_save_billing_rejects_already_paid(self):
        self.payment.response_code = '1'
        self.payment.response_reason_code = '1'
        self.payment.status_detail = 'approved'
        self.payment.save()

        response = self.client.post(self.url, {'zip': '12345'})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'already paid')

    def test_save_billing_rejects_payment_without_intent(self):
        payment = _make_payment(payment_intent_id='')
        url = reverse('stripe.save_billing', args=[payment.id, payment.guid])

        response = self.client.post(url, {'zip': '12345'})

        self.assertEqual(response.status_code, 403)


@override_settings(STRIPE_SECRET_KEY='sk_test_dummy')
class FinalizeViewTests(TestCase):
    def setUp(self):
        self.payment = _make_payment()
        self.url = reverse(
            'stripe.finalize', args=[self.payment.id, self.payment.guid])

    @staticmethod
    def _succeeded_intent(payment):
        return SimpleNamespace(
            status='succeeded',
            created=1786105095,
            latest_charge='ch_finalize_ok',
            customer=None,
            metadata=SimpleNamespace(
                tendenci_payment_id=str(payment.id),
                tendenci_payment_guid=payment.guid,
            ),
        )

    def test_finalize_redirects_when_no_intent_is_known(self):
        payment = _make_payment(payment_intent_id='')
        url = reverse('stripe.finalize', args=[payment.id, payment.guid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/payonline/', response['Location'])

    def test_finalize_falls_back_to_stored_intent_id(self):
        with patch('tendenci.apps.payments.stripe.views.configure_stripe'), \
                patch('tendenci.apps.payments.stripe.views.stripe.PaymentIntent.retrieve',
                      return_value=self._succeeded_intent(self.payment)) as retrieve, \
                patch.object(Invoice, 'make_payment', return_value=True):
            response = self.client.get(self.url)

        self.assertEqual(retrieve.call_args.args[0], 'pi_stored')
        self.assertIn('/thankyou/', response['Location'])
        self.payment.refresh_from_db()
        self.assertTrue(self.payment.is_approved)

    def test_finalize_accepts_intent_that_is_not_the_stored_one(self):
        """A second tab overwrites payment_intent_id; the first tab must still pay."""
        with patch('tendenci.apps.payments.stripe.views.configure_stripe'), \
                patch('tendenci.apps.payments.stripe.views.stripe.PaymentIntent.retrieve',
                      return_value=self._succeeded_intent(self.payment)) as retrieve, \
                patch.object(Invoice, 'make_payment', return_value=True):
            response = self.client.get(
                self.url, {'payment_intent': 'pi_from_other_tab'})

        self.assertEqual(retrieve.call_args.args[0], 'pi_from_other_tab')
        self.assertIn('/thankyou/', response['Location'])
        self.payment.refresh_from_db()
        self.assertTrue(self.payment.is_approved)

    def test_finalize_retrieves_from_standard_connected_account(self):
        with patch('tendenci.apps.payments.stripe.views.configure_stripe'), \
                patch('tendenci.apps.payments.stripe.views.stripe.PaymentIntent.retrieve',
                      return_value=self._succeeded_intent(self.payment)) as retrieve, \
                patch.object(Invoice, 'stripe_connected_account',
                             return_value=('acct_standard', 'standard')), \
                patch.object(Invoice, 'make_payment', return_value=True):
            self.client.get(self.url, {'payment_intent': 'pi_ok'})

        self.assertEqual(
            retrieve.call_args.kwargs['stripe_account'], 'acct_standard')

    def test_finalize_retrieves_from_platform_for_express(self):
        with patch('tendenci.apps.payments.stripe.views.configure_stripe'), \
                patch('tendenci.apps.payments.stripe.views.stripe.PaymentIntent.retrieve',
                      return_value=self._succeeded_intent(self.payment)) as retrieve, \
                patch.object(Invoice, 'stripe_connected_account',
                             return_value=('acct_express', 'express')), \
                patch.object(Invoice, 'make_payment', return_value=True):
            self.client.get(self.url, {'payment_intent': 'pi_ok'})

        self.assertNotIn('stripe_account', retrieve.call_args.kwargs)

    def test_finalize_rejects_metadata_mismatch(self):
        intent = SimpleNamespace(
            status='succeeded',
            metadata=SimpleNamespace(
                tendenci_payment_id='999',
                tendenci_payment_guid='wrong',
            ),
        )
        with patch('tendenci.apps.payments.stripe.views.configure_stripe'), \
                patch('tendenci.apps.payments.stripe.views.stripe.PaymentIntent.retrieve',
                      return_value=intent):
            response = self.client.get(
                self.url, {'payment_intent': 'pi_mismatch'})

        self.assertEqual(response.status_code, 302)
        self.assertIn('/payonline/', response['Location'])
        self.payment.refresh_from_db()
        self.assertFalse(self.payment.is_approved)

    def test_finalize_rejects_non_succeeded_status(self):
        intent = SimpleNamespace(
            status='processing',
            metadata=SimpleNamespace(
                tendenci_payment_id=str(self.payment.id),
                tendenci_payment_guid=self.payment.guid,
            ),
        )
        with patch('tendenci.apps.payments.stripe.views.configure_stripe'), \
                patch('tendenci.apps.payments.stripe.views.stripe.PaymentIntent.retrieve',
                      return_value=intent):
            response = self.client.get(
                self.url, {'payment_intent': 'pi_processing'})

        self.assertEqual(response.status_code, 302)
        self.assertIn('/payonline/', response['Location'])

    @patch('tendenci.apps.payments.stripe.views.send_payment_notice')
    @patch('tendenci.apps.payments.stripe.views.log_payment')
    @patch('tendenci.apps.payments.stripe.views.payment_processing_object_updates')
    def test_finalize_approves_succeeded_intent(
            self, mock_updates, mock_log, mock_notice):
        intent = self._succeeded_intent(self.payment)
        with patch('tendenci.apps.payments.stripe.views.configure_stripe'), \
                patch('tendenci.apps.payments.stripe.views.stripe.PaymentIntent.retrieve',
                      return_value=intent), \
                patch.object(Invoice, 'make_payment', return_value=True):
            response = self.client.get(
                self.url, {'payment_intent': 'pi_ok'})

        self.assertEqual(response.status_code, 302)
        self.assertIn('/thankyou/', response['Location'])
        self.payment.refresh_from_db()
        self.assertTrue(self.payment.is_approved)
        self.assertEqual(self.payment.trans_id, 'ch_finalize_ok')
        mock_updates.assert_called_once()
        mock_log.assert_called_once()
        mock_notice.assert_called_once()

    def test_finalize_redirects_thank_you_if_already_approved(self):
        self.payment.response_code = '1'
        self.payment.response_reason_code = '1'
        self.payment.status_detail = 'approved'
        self.payment.save()

        response = self.client.get(
            self.url, {'payment_intent': 'pi_anything'})

        self.assertEqual(response.status_code, 302)
        self.assertIn('/thankyou/', response['Location'])


class PaymentMethodCodeTests(SimpleTestCase):
    def test_google_pay_and_payto_and_plain_card(self):
        google = SimpleNamespace(
            latest_charge=SimpleNamespace(
                payment_method_details={
                    'type': 'card',
                    'card': {'wallet': {'type': 'google_pay'}},
                },
            ),
        )
        payto = SimpleNamespace(
            latest_charge=SimpleNamespace(
                payment_method_details=SimpleNamespace(type='payto'),
            ),
        )
        card = SimpleNamespace(
            latest_charge=SimpleNamespace(
                payment_method_details=SimpleNamespace(
                    type='card', card=SimpleNamespace(wallet=None)),
            ),
        )

        self.assertEqual(payment_method_code_from_intent(google), 'googlepay')
        self.assertEqual(payment_method_code_from_intent(payto), 'payto')
        self.assertEqual(payment_method_code_from_intent(card), '')

    def test_unexpanded_charge_uses_payment_method(self):
        intent = SimpleNamespace(
            latest_charge='ch_1',
            payment_method=SimpleNamespace(
                type='payto',
                payto=SimpleNamespace(last4='1234'),
            ),
        )
        self.assertEqual(payment_method_code_from_intent(intent), 'payto')


class UserFacingStripeMessageTests(SimpleTestCase):
    def test_card_decline_keeps_plain_stripe_message(self):
        import stripe
        exc = stripe.error.CardError(
            'Your card was declined.', 'number', 'card_declined')

        self.assertEqual(
            user_facing_stripe_message(exc, 'fallback'),
            'Your card was declined.',
        )

    def test_json_body_is_replaced(self):
        import stripe
        payload = (
            '{"error": {"message": "No such payment_intent", '
            '"request_log_url": "https://dashboard.stripe.com/logs/req_1"}}'
        )
        exc = stripe.error.InvalidRequestError(payload, 'payment_intent')

        self.assertEqual(
            user_facing_stripe_message(exc, 'Please try again.'),
            'Please try again.',
        )

    def test_card_error_with_json_message_uses_fallback(self):
        import stripe
        exc = stripe.error.CardError(
            '{"error": {"message": "raw"}}', None, 'card_declined')

        self.assertEqual(
            user_facing_stripe_message(exc, 'Your card was declined.'),
            'Your card was declined.',
        )
