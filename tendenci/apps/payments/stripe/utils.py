import math

from django.conf import settings

from tendenci import __version__ as tendenci_version
from tendenci.apps.site_settings.utils import get_setting


def stripe_set_app_info(stripe):
    stripe.set_app_info(
    "Tendenci Stripe Plugin",
    version=tendenci_version,
    url="https://www.tendenci.com",
    partner_id="pp_partner_FcOFsMQDoGeT1B"
)


def configure_stripe(stripe_module):
    """Set API key, API version, and partner app info for Stripe requests."""
    stripe_module.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    stripe_module.api_version = settings.STRIPE_API_VERSION
    stripe_set_app_info(stripe_module)


def build_payment_intent_params(payment, currency, customer_id=None,
                                setup_future_usage=None):
    """Build PaymentIntent.create kwargs. Never set payment method types (use Dashboard dynamic methods)."""
    params = {
        'amount': math.trunc(payment.amount * 100),
        'currency': currency,
        'description': payment.description,
        'metadata': {
            'tendenci_payment_id': str(payment.id),
            'tendenci_payment_guid': payment.guid,
        },
    }

    if customer_id:
        params['customer'] = customer_id
    if setup_future_usage:
        params['setup_future_usage'] = setup_future_usage

    connected_account_id, scope = payment.invoice.stripe_connected_account()
    if connected_account_id:
        import stripe as stripe_module
        stripe_module.client_id = get_setting(
            'module', 'payments', 'stripe_connect_client_id')
        if scope == 'express':
            application_fee = payment.invoice.get_stripe_application_fee(
                payment.amount)
            params.update({
                'application_fee_amount': math.trunc(application_fee * 100),
                'transfer_data': {'destination': connected_account_id},
            })
        else:
            params['stripe_account'] = connected_account_id

    return params


def _charge_id_from_intent(payment_intent):
    latest_charge = getattr(payment_intent, 'latest_charge', None)
    if not latest_charge:
        return ''
    if isinstance(latest_charge, str):
        return latest_charge
    return getattr(latest_charge, 'id', '') or ''


def _stripe_object_id(value):
    if not value:
        return ''
    if isinstance(value, str):
        return value
    return getattr(value, 'id', '') or ''


def _failed_off_session_response(message, code=''):
    text = (message or '')[:200]
    return {
        'status_detail': 'not approved',
        'response_code': '0',
        'response_reason_code': '0',
        'result_code': 'Error',
        'message_code': code or '',
        'message_text': text,
        'response_reason_text': message or '',
    }


def connected_account_request_options(payment):
    """
    Request options identifying the account a PaymentIntent is created on.

    Express accounts are charged on the platform (via transfer_data), so only
    standard accounts need stripe_account.
    """
    connected_account_id, scope = payment.invoice.stripe_connected_account()
    if connected_account_id and scope != 'express':
        return {'stripe_account': connected_account_id}
    return {}


def customer_off_session_payment_method_id(stripe_module, customer_id,
                                           request_options=None):
    """Return a reusable PaymentMethod or legacy source id for off-session charges."""
    if not customer_id:
        return ''

    request_options = request_options or {}
    customer = stripe_module.Customer.retrieve(customer_id, **request_options)
    invoice_settings = getattr(customer, 'invoice_settings', None)
    default_pm = _stripe_object_id(
        getattr(invoice_settings, 'default_payment_method', None)
        if invoice_settings else None
    )
    if default_pm:
        return default_pm

    try:
        listed = stripe_module.PaymentMethod.list(
            customer=customer_id, limit=10, **request_options)
    except stripe_module.InvalidRequestError:
        # API versions before 2022-08-01 require an explicit type.
        listed = stripe_module.PaymentMethod.list(
            customer=customer_id, type='card', limit=10, **request_options)
    payment_methods = getattr(listed, 'data', None) or []

    if payment_methods:
        return _stripe_object_id(payment_methods[0])

    return _stripe_object_id(getattr(customer, 'default_source', None))


def charge_customer_off_session(stripe_module, payment, customer_id,
                                description=None, idempotency_key=None):
    """
    Confirm an off-session PaymentIntent for a saved customer.

    Returns (success, response_d). Does not set payment_method_types.
    """
    configure_stripe(stripe_module)
    currency = get_setting('site', 'global', 'currency')

    try:
        payment_method_id = customer_off_session_payment_method_id(
            stripe_module, customer_id,
            request_options=connected_account_request_options(payment))
    except Exception as e:
        return False, _failed_off_session_response(str(e))

    if not payment_method_id:
        return False, _failed_off_session_response(
            'No payment method is on file for this customer.')

    params = build_payment_intent_params(
        payment, currency, customer_id=customer_id)
    if description:
        params['description'] = description
    params['payment_method'] = payment_method_id
    params['confirm'] = True
    params['off_session'] = True
    # Unattended retries must not charge the member twice.
    if idempotency_key:
        params['idempotency_key'] = idempotency_key

    try:
        payment_intent = stripe_module.PaymentIntent.create(**params)
    except stripe_module.CardError as e:
        json_body = getattr(e, 'json_body', None) or {}
        err = json_body.get('error') if isinstance(json_body, dict) else None
        err = err or {}
        code = err.get('code') or getattr(e, 'code', '') or ''
        message = (
            err.get('message')
            or getattr(e, 'user_message', None)
            or str(e)
        )
        text = '{message} status={status}, code={code}'.format(
            message=message,
            status=getattr(e, 'http_status', ''),
            code=code,
        )
        response = _failed_off_session_response(text, code=code)
        response['payment_method_id'] = payment_method_id
        return False, response
    except Exception as e:
        response = _failed_off_session_response(str(e))
        response['payment_method_id'] = payment_method_id
        return False, response

    if getattr(payment_intent, 'status', None) == 'succeeded':
        return True, {
            'status_detail': 'approved',
            'response_code': '1',
            'response_subcode': '1',
            'response_reason_code': '1',
            'response_reason_text': (
                'This transaction has been approved. (Created# %s)'
                % payment_intent.created
            ),
            'trans_id': _charge_id_from_intent(payment_intent),
            'result_code': 'Ok',
            'message_code': '',
            'message_text': 'Successful.',
            'payment_method_id': payment_method_id,
        }

    response = _failed_off_session_response(
        'PaymentIntent status=%s' % getattr(payment_intent, 'status', ''))
    response['payment_method_id'] = payment_method_id
    response['trans_id'] = _charge_id_from_intent(payment_intent)
    return False, response


def payment_update_from_intent(request, payment_intent, payment):
    """Approve a Payment from a succeeded PaymentIntent; store Charge id."""
    if getattr(payment_intent, 'status', None) == 'succeeded':
        payment.status_detail = 'approved'
        payment.response_code = '1'
        payment.response_subcode = '1'
        payment.response_reason_code = '1'
        payment.response_reason_text = (
            'This transaction has been approved. (Created# %s)'
            % payment_intent.created
        )
        payment.trans_id = _charge_id_from_intent(payment_intent)
    else:
        payment.response_code = 0
        payment.response_reason_code = 0
        payment.response_reason_text = (
            'PaymentIntent status=%s' % getattr(payment_intent, 'status', '')
        )

    if payment.is_approved:
        payment.mark_as_paid()
        payment.save()
        payment.invoice.make_payment(request.user, payment.amount)
    else:
        if payment.status_detail == '':
            payment.status_detail = 'not approved'
        payment.save()


def payment_update_stripe(request, charge_response, payment):
    if hasattr(charge_response,'paid') and charge_response.paid:
        payment.status_detail = 'approved'
        payment.response_code = '1'
        payment.response_subcode = '1'
        payment.response_reason_code = '1'
        payment.response_reason_text = 'This transaction has been approved. (Created# %s)' % charge_response.created
        payment.trans_id = charge_response.id
    else:
        payment.response_code = 0
        payment.response_reason_code = 0
        payment.response_reason_text = charge_response

    if payment.is_approved:
        payment.mark_as_paid()
        payment.save()
        payment.invoice.make_payment(request.user, payment.amount)
    else:
        if payment.status_detail == '':
            payment.status_detail = 'not approved'
        payment.save()
