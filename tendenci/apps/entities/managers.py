from django.contrib.auth.models import AnonymousUser
from django.db import models


class EntityManager(models.Manager):
    def first(self, **kwargs):
        """
        Returns first instance that matches filters.
        If no instance is found then a none type object is returned.
        """
        [instance] = self.filter(**kwargs).order_by('pk')[:1] or [None]
        return instance

    def get_or_create_default(self, user=AnonymousUser()):
        from tendenci.core.site_settings.utils import get_global_setting
        entity = self.first()
        if not entity:
            params = {'id': 1,
                      'entity_name': get_global_setting('sitedisplayname') or 'Tendenci',
                      'entity_type': '',
                      'contact_name': get_global_setting('sitecontactname'),
                      'phone': get_global_setting('sitephonenumber'),
                      'email': get_global_setting('sitecontactemail'),
                      'fax': '',
                      'website': get_global_setting('siteurl'),
                      'summary': '',
                      'notes': '',
                      'admin_notes': 'system auto created',
                      'allow_anonymous_view': True,
                      'status': True,
                      'status_detail': 'active'
                      }
            if not user.is_anonymous():
                params.update({'creator': user,
                               'creator_username': user.username,
                               'owner': user,
                               'owner_username': user.username
                               })
            else:
                params.update({'creator_username': '',
                               'owner_username': ''
                               })
            entity = self.create(**params)

        return entity
