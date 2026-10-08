"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from datetime import timedelta
from contextlib import redirect_stdout
from io import StringIO

from django.core.management import call_command
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from tendenci.apps.directories.models import Directory, DirectoryPricing

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


class UnlimitedDurationTest(TestCase):
    """
    A requested duration of 0 is the "Unlimited" pricing option,
    so the directory should never expire.
    """
    @classmethod
    def setUpTestData(cls):
        # load the default site settings (directories, profiles, etc.)
        with redirect_stdout(StringIO()):
            call_command('update_settings', verbosity=0)

    def setUp(self):
        self.superuser = User.objects.create_superuser('dir_admin', 'dir_admin@example.com', 'password')
        self.client = Client()
        self.client.login(username='dir_admin', password='password')
        self.unlimited_pricing = DirectoryPricing.objects.create(duration=0)
        self.pricing_30 = DirectoryPricing.objects.create(duration=30)

    def make_directory(self, **kwargs):
        defaults = {
            'headline': 'Unit Testing',
            'slug': 'unit-testing-%s' % Directory.objects.count(),
            'creator': self.superuser,
            'creator_username': self.superuser.username,
            'owner': self.superuser,
            'owner_username': self.superuser.username,
            'status': True,
            'status_detail': 'active',
            'enclosure_length': 0,
        }
        defaults.update(kwargs)
        return Directory.objects.create(**defaults)

    def test_get_expiration_dt_unlimited(self):
        directory = self.make_directory(activation_dt=timezone.now(), requested_duration=0)
        self.assertIsNone(directory.get_expiration_dt())

    def test_get_expiration_dt_limited(self):
        now = timezone.now()
        directory = self.make_directory(activation_dt=now, requested_duration=30)
        self.assertEqual(directory.get_expiration_dt(), now + timedelta(days=30))

    def test_approve_unlimited_does_not_expire(self):
        directory = self.make_directory(requested_duration=0, status_detail='pending')
        response = self.client.post(reverse('directory.approve', args=[directory.pk]))
        self.assertEqual(response.status_code, 302)
        directory.refresh_from_db()
        self.assertEqual(directory.status_detail, 'active')
        self.assertIsNotNone(directory.activation_dt)
        self.assertIsNone(directory.expiration_dt)

    def test_approve_limited_expires_after_duration(self):
        directory = self.make_directory(requested_duration=30, status_detail='pending')
        self.client.post(reverse('directory.approve', args=[directory.pk]))
        directory.refresh_from_db()
        self.assertEqual(directory.expiration_dt, directory.activation_dt + timedelta(days=30))

    def add_directory(self, pricing):
        return self.client.post(reverse('directory.add'), {
            'headline': 'Added %s' % pricing.duration,
            'slug': 'added-%s' % pricing.duration,
            'activation_dt_0': timezone.now().strftime('%Y-%m-%d'),
            'activation_dt_1': '00:00:00',
            'summary': 'summary',
            'body': 'body',
            'pricing': pricing.pk,
            'timezone': 'America/Chicago',
            'status_detail': 'active',
            'email': 'dir_admin@example.com',
        })

    def test_add_unlimited_does_not_expire(self):
        response = self.add_directory(self.unlimited_pricing)
        self.assertEqual(response.status_code, 302)
        directory = Directory.objects.get(headline='Added 0')
        self.assertEqual(directory.requested_duration, 0)
        self.assertIsNone(directory.expiration_dt)

    def test_add_limited_expires_after_duration(self):
        response = self.add_directory(self.pricing_30)
        self.assertEqual(response.status_code, 302)
        directory = Directory.objects.get(headline='Added 30')
        self.assertEqual(directory.requested_duration, 30)
        self.assertEqual(directory.expiration_dt, directory.activation_dt + timedelta(days=30))

    def test_edit_keeps_unlimited_and_limited_expiration(self):
        now = timezone.now().replace(microsecond=0)
        for pricing, expected in ((self.unlimited_pricing, None),
                                  (self.pricing_30, now + timedelta(days=30))):
            directory = self.make_directory(activation_dt=now, requested_duration=7)
            response = self.client.post(reverse('directory.edit', args=[directory.pk]), {
                'headline': directory.headline,
                'slug': directory.slug,
                'summary': 'summary',
                'body': 'body',
                'pricing': pricing.pk,
                'timezone': 'America/Chicago',
                'status_detail': 'active',
                'activation_dt_0': now.strftime('%Y-%m-%d'),
                'activation_dt_1': now.strftime('%H:%M:%S'),
            })
            self.assertEqual(response.status_code, 302)
            directory.refresh_from_db()
            self.assertEqual(directory.requested_duration, pricing.duration)
            self.assertEqual(directory.expiration_dt, expected)

    def test_renew_unlimited_does_not_expire(self):
        directory = self.make_directory(activation_dt=timezone.now() - timedelta(days=60),
                                        requested_duration=30,
                                        expiration_dt=timezone.now() - timedelta(days=30))
        response = self.client.post(reverse('directory.renew', args=[directory.pk]), {
            'pricing': self.unlimited_pricing.pk,
        })
        self.assertEqual(response.status_code, 302)
        directory.refresh_from_db()
        self.assertEqual(directory.requested_duration, 0)
        self.assertIsNone(directory.expiration_dt)

    def test_renewal_notices_skip_unlimited(self):
        self.make_directory(activation_dt=timezone.now(), requested_duration=0, expiration_dt=None)
        limited = self.make_directory(activation_dt=timezone.now(), requested_duration=14,
                                      expiration_dt=timezone.now() + timedelta(days=1))
        with redirect_stdout(StringIO()):
            call_command('send_directory_notices')
        self.assertTrue(Directory.objects.get(pk=limited.pk).renewal_notice_sent)
