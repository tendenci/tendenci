from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase, override_settings
from simple_salesforce.exceptions import SalesforceAuthenticationFailed

from tendenci.apps.base.utils import get_salesforce_access

SALESFORCE_SETTINGS = (
    'SALESFORCE_USERNAME',
    'SALESFORCE_PASSWORD',
    'SALESFORCE_SECURITY_TOKEN',
    'SALESFORCE_CONSUMER_KEY',
    'SALESFORCE_PRIVATEKEY_FILE',
    'SALESFORCE_PRIVATEKEY',
    'SALESFORCE_SANDBOX',
    'SALESFORCE_DOMAIN',
)

USERNAME = 'integration@example.org'
CONSUMER_KEY = 'test-consumer-key'
PRIVATEKEY_FILE = '/path/to/salesforce.key'
PRIVATEKEY = '-----BEGIN PRIVATE KEY-----\nnot-a-real-key\n-----END PRIVATE KEY-----'

JWT_SETTINGS = {
    'SALESFORCE_USERNAME': USERNAME,
    'SALESFORCE_CONSUMER_KEY': CONSUMER_KEY,
    'SALESFORCE_PRIVATEKEY_FILE': PRIVATEKEY_FILE,
}

LEGACY_SETTINGS = {
    'SALESFORCE_USERNAME': USERNAME,
    'SALESFORCE_PASSWORD': 'test-password',
    'SALESFORCE_SECURITY_TOKEN': 'test-token',
}


@patch('tendenci.apps.base.utils.Salesforce', autospec=True)
class GetSalesforceAccessTest(SimpleTestCase):
    """
    get_salesforce_access() picks the JWT or the legacy login from settings.
    Salesforce is mocked with autospec, so a keyword argument that
    simple-salesforce does not accept (such as sandbox=) fails the test.
    """
    def setUp(self):
        # Start each test with no Salesforce settings, whatever the site has.
        no_salesforce = override_settings()
        no_salesforce.enable()
        self.addCleanup(no_salesforce.disable)
        for name in SALESFORCE_SETTINGS:
            delattr(settings, name)

    def get_access(self, **salesforce_settings):
        with self.settings(**salesforce_settings), redirect_stdout(StringIO()) as output:
            sf = get_salesforce_access()
        return sf, output.getvalue()

    def test_jwt_with_key_file(self, mock_salesforce):
        sf, _ = self.get_access(**JWT_SETTINGS)

        self.assertEqual(sf, mock_salesforce.return_value)
        mock_salesforce.assert_called_once_with(username=USERNAME,
                                                consumer_key=CONSUMER_KEY,
                                                privatekey_file=PRIVATEKEY_FILE,
                                                privatekey=None,
                                                domain='login')

    def test_jwt_with_inline_key_on_sandbox(self, mock_salesforce):
        sf, _ = self.get_access(SALESFORCE_USERNAME=USERNAME,
                                SALESFORCE_CONSUMER_KEY=CONSUMER_KEY,
                                SALESFORCE_PRIVATEKEY=PRIVATEKEY,
                                SALESFORCE_SANDBOX=True)

        self.assertEqual(sf, mock_salesforce.return_value)
        mock_salesforce.assert_called_once_with(username=USERNAME,
                                                consumer_key=CONSUMER_KEY,
                                                privatekey_file=None,
                                                privatekey=PRIVATEKEY,
                                                domain='test')

    def test_jwt_preferred_over_legacy(self, mock_salesforce):
        sf, _ = self.get_access(**{**LEGACY_SETTINGS, **JWT_SETTINGS})

        self.assertEqual(sf, mock_salesforce.return_value)
        mock_salesforce.assert_called_once_with(username=USERNAME,
                                                consumer_key=CONSUMER_KEY,
                                                privatekey_file=PRIVATEKEY_FILE,
                                                privatekey=None,
                                                domain='login')

    def test_legacy_login(self, mock_salesforce):
        sf, _ = self.get_access(**LEGACY_SETTINGS)

        # Before #1443 this passed sandbox=, which simple-salesforce 1.x
        # rejects with a TypeError, so the function always returned None.
        self.assertEqual(sf, mock_salesforce.return_value)
        mock_salesforce.assert_called_once_with(username=USERNAME,
                                                password='test-password',
                                                security_token='test-token',
                                                domain='login')

    def test_legacy_login_on_sandbox(self, mock_salesforce):
        sf, _ = self.get_access(SALESFORCE_SANDBOX=True, **LEGACY_SETTINGS)

        self.assertEqual(sf, mock_salesforce.return_value)
        mock_salesforce.assert_called_once_with(username=USERNAME,
                                                password='test-password',
                                                security_token='test-token',
                                                domain='test')

    def test_domain_setting_overrides_sandbox_for_jwt(self, mock_salesforce):
        self.get_access(SALESFORCE_SANDBOX=True, SALESFORCE_DOMAIN='example.my', **JWT_SETTINGS)

        self.assertEqual(mock_salesforce.call_args.kwargs['domain'], 'example.my')

    def test_domain_setting_overrides_sandbox_for_legacy(self, mock_salesforce):
        self.get_access(SALESFORCE_SANDBOX=True, SALESFORCE_DOMAIN='example.my', **LEGACY_SETTINGS)

        self.assertEqual(mock_salesforce.call_args.kwargs['domain'], 'example.my')

    def test_no_settings(self, mock_salesforce):
        sf, _ = self.get_access()

        self.assertIsNone(sf)
        mock_salesforce.assert_not_called()

    def test_consumer_key_without_private_key(self, mock_salesforce):
        sf, _ = self.get_access(SALESFORCE_USERNAME=USERNAME,
                                SALESFORCE_CONSUMER_KEY=CONSUMER_KEY)

        self.assertIsNone(sf)
        mock_salesforce.assert_not_called()

    def test_jwt_authentication_failure(self, mock_salesforce):
        mock_salesforce.side_effect = SalesforceAuthenticationFailed(
            'invalid_grant', "user hasn't approved this consumer")

        sf, output = self.get_access(**JWT_SETTINGS)

        self.assertIsNone(sf)
        self.assertIn('Salesforce authentication failed', output)

    def test_legacy_authentication_failure(self, mock_salesforce):
        mock_salesforce.side_effect = SalesforceAuthenticationFailed(
            'INVALID_LOGIN', 'Invalid username, password, security token; or user locked out.')

        sf, output = self.get_access(**LEGACY_SETTINGS)

        self.assertIsNone(sf)
        self.assertIn('Salesforce authentication failed', output)
