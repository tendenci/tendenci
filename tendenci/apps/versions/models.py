# models.py
from dateutil.parser import parse

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
import json

from tendenci.apps.versions.managers import VersionManager


class Version(models.Model):
    """
    Creates a historical version of an object.
    Stores the creator, create_dt, and the object serialized in json
    """

    create_dt = models.DateTimeField(_('create time'))
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField(_('object id'))
    object_repr = models.CharField(_('object repr'), max_length=200)
    object_changes = models.TextField(_('change message'), blank=True)
    object_value = models.TextField(_('changed object'), blank=True)
    hash = models.CharField(max_length=40, null=True, default='')

    _object = GenericForeignKey('content_type', 'object_id')

    objects = VersionManager()

    class Meta:
        app_label = 'versions'

    def get_object(self):
        _object = None
        try:
            _object = self._object
        except:
            pass
        return _object

    def get_version_object(self):
        data = json.loads(self.object_value)['fields']
        obj_data = {'pk': self.object_id}
        for f in self.get_object()._meta.fields:
            field_name = unicode(f.name)
            if field_name in data:
                #print unicode(f.get_internal_type())
                if unicode(f.get_internal_type()) == 'ForeignKey' or unicode(f.get_internal_type()) == 'OneToOneField':
                    obj_data[field_name + "_id"] = data[field_name]
                elif unicode(f.get_internal_type()) == 'DateTimeField':
                    obj_data[field_name] = parse(data[field_name])
                else:
                    obj_data[field_name] = data[field_name]
        obj = self.get_object().__class__(**obj_data)

        return obj

    def get_object_version_url(self):
        try:
            return self.get_version_object().get_version_url(self.hash)
        except:
            return ''
