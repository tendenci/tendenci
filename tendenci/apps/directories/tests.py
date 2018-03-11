"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from builtins import int

from django.test import TestCase, Client
from django.contrib.auth.models import User

from tendenci.apps.directories.models import Directory

class DirectoryTest(TestCase):
    def setUp(self):
        # create the objects needed
        self.client = Client()
        self.directory = Directory()

        self.user = User(username='admin')
        self.user.set_password('google')
        self.user.is_active = True
        self.user.save()

    def tearDown(self):
        self.client = None
        self.directory = None
        self.user = None

    def test_save(self):
        self.directory.headline = 'Unit Testing'
        self.directory.summary = 'Unit Testing'

        # required fields
        self.directory.creator = self.user
        self.directory.creator_username = self.user.username
        self.directory.owner = self.user
        self.directory.owner_username = self.user.username
        self.directory.status = True
        self.directory.status_detail = 'active'
        self.directory.enclosure_length = 0
        self.directory.timezone = 'America/Chicago'

        self.directory.save()

        self.assertTrue(isinstance(self.directory.id, int))
