
import random
import time
import hashlib
import sys

from django.core.management.base import BaseCommand
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpRequest

class Command(BaseCommand):
    """
    example: python manage.py event_register 4
    """
    user_count = User.objects.count()

    def add_arguments(self, parser):
        parser.add_argument('-e', '--event',
            action='store',
            dest='event',
            default=None,
            type='int',
            help='The event-id of the event where you wish to add registrants'
        )
        parser.add_argument('-l', '--limit',
            action='store',
            dest='limit',
            default=1,
            type='int',
            help='The number of registrants you would like to make'
        )

    def handle(self, *event_ids, **options):
        from tendenci.apps.events.models import Event, PaymentMethod
        from tendenci.apps.events.utils import save_registration

        #event_kwargs = {
        #    'entity': 1,
        #    'type': 1,
        #    'title': 'Some Event',
        #    'description': 'Some description',
        #    'all_day': True,
        #    'start_dt': datetime.datetime.now(),
        #    'end_dt': datetime.datetime.now(),
        #    'timezone': 1,
        #    'place': 1,
        #}

        event_id = options['event']
        limit = options['limit']

        if event_id: event = Event.objects.get(pk=event_id)
        else: event = Event.objects.latest('pk')

        price = event.registration_configuration.price

        # print title & URL
        print('Event: %s' % event.title, event.get_absolute_url())

        for n in range(limit):
            request = self.random_request
            save_registration(user=request.user, event=event,
                payment_method=PaymentMethod.objects.get(pk=3), price=price)

            # print registrant
            print(n+1, '%s (registrant)' % request.user)

    @property
    def random_session_key(self):
        session_key = hashlib.md5.new((
            str(random.randint(0, sys.maxsize - 1)) + "#" +
            str(random.randint(0, sys.maxsize - 1)) + "#" +
            str(time.time()) + "#").encode()).hexdigest()
        return session_key

    @property
    def random_request(self):

        random_index = int(random.random() * self.user_count) + 1
        user = User.objects.get(pk=random_index)
        user.backend = 'some.random.set.of.characters'
        request = HttpRequest()
        request.user = user
        request.session = SessionStore(session_key=self.random_session_key)
        login(request, request.user)

        return request
