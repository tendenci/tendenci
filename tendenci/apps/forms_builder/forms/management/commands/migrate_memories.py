#!/usr/bin/env python
# vim:fileencoding=utf-8
import re
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from tendenci.apps.forms_builder.forms.models import Form, Field, FieldMemory

# The field in which Django stroed a logged in users ID if there is one.
# The key is not present in the session data if it's an anonymous session
session_uid_field = '_auth_user_id'

class Command(BaseCommand):
    args = ''
    help = 'Migrate session stored form memories to model stored form memories'

    def handle(self, *args, **options):
        '''
        Legacy form memories were stored in the Django session. Now they have their
        own model to make it easier to find them, and manage them. So as not to lose
        existing form memories, they can be migrated.

        Legacy memories are stored in the session with a key that identified the form
        and field and found by checked all session objects.
        '''
        session_cookie_age = settings.SESSION_COOKIE_AGE

        for form in Form.objects.all():
            if form.has_memory:
                self.stdout.write(f"Migrating memories for form: '{form.slug}'")
                key_pattern = re.compile(f"{form.slug}.field_(?P<field_id>\d+)")

                s_mem = [s for s in Session.objects.all()
                            if any([key for key in s.get_decoded() if re.match(key_pattern, key)])]

                self.stdout.write(f"\t{len(s_mem)} memories to migrate.")

                for s in s_mem:
                    uid = s.get_decoded().get(session_uid_field, None)

                    if not uid is None:
                        try:
                            user = User.objects.get(id=uid)
                        except User.DoesNotExist:
                            user = None
                    else:
                        user = None

                    for key, val in s.get_decoded().items():
                        key_match = re.match(key_pattern, key)
                        if key_match:
                            field_id = key_match["field_id"]
                            try:
                                field = form.fields.get(id=field_id)
                                # Django sessions only store an expiration date, which was calculated
                                # from at creation time, by adding the SESSION_COOKIE_AGE (in seconds)
                                # so we can only infer the save time by removing that. Not 100% reliable
                                # as the setting may have changed since it was saved, but the best we can do.
                                save_dt = s.expire_date - timedelta(seconds=session_cookie_age)

                                existing = FieldMemory.objects.filter(user=uid, session=s, field=field)

                                if existing:
                                    memory = existing[0]
                                    memory.user = user
                                    memory.session = s
                                    memory.field = field
                                    memory.val = val
                                    memory.save_dt = save_dt
                                else:
                                    memory = FieldMemory(user=user, session=s, field=field, value=val, save_dt=save_dt)

                                memory.save()
                            except Field.DoesNotExist:
                                pass

        self.stdout.write(f"Migrating memories completed successfully.")