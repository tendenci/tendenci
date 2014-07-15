"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User

from tendenci.addons.locations.models import Location

class LocationLocationTest(TestCase):
    def setUp(self):
        # create the objects needed
        self.client = Client()
        self.location = Location()

        self.user = User(username='admin')
        self.user.set_password('google')
        self.user.is_active = True
        self.user.save()


    def tearDown(self):
        self.client = None
        self.location = None
        self.user = None

    def test_save(self):
        self.location.location_name = 'Unit Testing'
        self.location.description = 'Unit Testing'

        # required fields
        self.location.creator = self.user
        self.location.creator_username = self.user.username
        self.location.owner = self.user
        self.location.owner_username = self.user.username
        self.location.status = True
        self.location.status_detail = 'active'
        self.location.enclosure_length = 0
        self.location.timezone = 'America/Chicago'

        self.location.save()

        self.assertEquals(type(self.location.id), long)


