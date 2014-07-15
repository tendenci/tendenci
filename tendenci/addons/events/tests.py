import logging

from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from tendenci.addons.events.models import RegConfPricing, Event, Addon
from tendenci.addons.events.views import delete_addon


handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)


logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class EventTest(TestCase):

    def setUp(self):
        self.pricing = RegConfPricing()

    def tearDown(self):
        self.pricing = None

    def test_pricing_description(self):
        self.pricing.title = "Test Pricing"
        self.pricing.price = 10.00
        self.pricing.allow_anonymous = True
        self.pricing.allow_user = True
        self.pricing.allow_member = True
        self.pricing.save()

        logger.info('Testing existence of description field')
        self.assertTrue(hasattr(self.pricing, 'description'))
        logger.info('Complete.')

        sample_description = "Test Description"
        self.pricing.description = sample_description
        self.pricing.save()

        logger.info('Testing description field update')
        self.assertTrue(self.pricing.description == sample_description)
        logger.info('Complete.')


class AdddonDeleteTest(TestCase):

    def create_test_superuser(self):
        self.client = Client()
        self.username = 'tester'
        self.email = 'test@test.com'
        self.password = 'test'
        User.objects.create_superuser(self.username, self.email, self.password)
        self.client.login(username=self.username, password=self.password)

    def setUp(self):
        self.event = Event()
        self.addon = Addon()

    def tearDown(self):
        self.event = None
        self.addon = None
        self.client = None
        self.username = None
        self.email = None
        self.password = None

    def create_instances(self):
        self.event.title = 'Test Event'
        self.event.save()
        self.addon.title = 'Test Addon'
        self.addon.event = self.event
        self.addon.save()

    def test_delete_addon_method(self):
        self.create_instances()
        addon_pk = self.addon.pk

        logger.info('Testing new delete method of Addon model.')
        self.addon.delete(from_db=True)
        with self.assertRaises(Addon.DoesNotExist):
            Addon.objects.get(pk=addon_pk)
        with self.assertRaises(Addon.DoesNotExist):
            Addon.objects.get(title='Test Addon')
        logger.info('Complete.')

    def test_delete_addon_view(self):
        self.create_instances()
        self.create_test_superuser()
        addon_pk = self.addon.pk
        delete_addon_link = reverse(
            'event.delete_addon',
            kwargs={'event_id': self.event.id, 'addon_id': addon_pk})

        response = self.client.get(delete_addon_link)
        logger.info('Testing new delete addon view.')
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Addon.DoesNotExist):
            Addon.objects.get(pk=addon_pk)
        with self.assertRaises(Addon.DoesNotExist):
            Addon.objects.get(title='Test Addon')
        logger.info('Complete.')