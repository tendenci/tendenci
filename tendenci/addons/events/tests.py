import logging

from django.test import TestCase

from tendenci.addons.events.models import RegConfPricing


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

