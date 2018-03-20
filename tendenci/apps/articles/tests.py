"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from builtins import int

from django.test import TestCase, Client
from django.contrib.auth.models import User

from tendenci.apps.articles.models import Article

class ArticleTest(TestCase):
    def setUp(self):
        # create the objects needed
        self.client = Client()
        self.article = Article()

        self.user = User(username='admin')
        self.user.set_password('google')
        self.user.is_active = True
        self.user.save()

    def tearDown(self):
        self.client = None
        self.article = None
        self.user = None

    def test_save(self):
        self.article.headline = 'Unit Testing'
        self.article.summary = 'Unit Testing'

        # required fields
        self.article.creator = self.user
        self.article.creator_username = self.user.username
        self.article.owner = self.user
        self.article.owner_username = self.user.username
        self.article.status = True
        self.article.status_detail = 'active'
        self.article.enclosure_length = 0
        self.article.timezone = 'America/Chicago'

        self.article.save()

        self.assertTrue(isinstance(self.article.id, int))
