from unittest import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.test.simple import DjangoTestSuiteRunner
from django.contrib.auth.models import User
from django.conf import settings


class NoDbTestRunner(DjangoTestSuiteRunner):
    """
    A test runner to test withouth database creation
    """

    def setup_databases(self, **kwargs):
        """
        Override the database creation defined in parent class
        """
        pass

    def teardown_databases(self, old_config, **kwargs):
        """
        Override the database teardown defined in parent class
        """
        pass


class TestCase(TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.get_or_create_user()
        self.sign_in()

    def tearDown(self):
        # self.delete_user()
        self.browser.quit()

    def get_or_create_user(self):
        from uuid import uuid1

        if not hasattr(settings, 'TEST_USER'):
            raise Exception('TEST_USER required in local_settings')

        try:
            user = User.objects.get(
                username=settings.TEST_USER['username'],
            )
        except User.DoesNotExist:
            user = User.objects.create_user(
                settings.TEST_USER['username'],
                settings.TEST_USER['email'],
                settings.TEST_USER['password'] or uuid1().get_hex()
            )

        user.first_name = settings.TEST_USER['first_name']
        user.last_name = settings.TEST_USER['last_name']

        user.is_authenticated = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        user.save()

        self.user = user

    def delete_user(self):
        self.user.delete()

    def sign_in(self):
        self.browser.get('http://127.0.0.1:8000/accounts/login/')
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys(self.user.username)
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys(self.user.password)
        password_field.send_keys(Keys.RETURN)

    def save_screenshot(self):
        relative_url = self.browser.current_url.replace('http://127.0.0.1:8000', '')
        relative_url = relative_url.replace('/', '_')
        relative_url = relative_url.strip('_')

        self.browser.save_screenshot(
            '%s%s.jpg' % (settings.TEST_SCREENSHOTS, relative_url)
        )




