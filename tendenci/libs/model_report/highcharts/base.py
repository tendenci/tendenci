# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy
from django.utils.encoding import force_unicode


true = 'true'
false = 'false'
null = 'null'
undefined = 'undefined'
Solid = 'Solid'
outside = 'outside'


_ = lambda s: force_unicode(ugettext_lazy(s))


class CollectionObject(object):
    _dicts = null

    def __init__(self):
        self._dicts = []

    def add(self, obj):
        self._dicts.append(obj)

    def __repr__(self):
        return unicode(self._dicts)


class DictObject:

    def __init__(self, **default):
        x = dict([(k, v if isinstance(v, (DictObject, CollectionObject)) else null) for k, v in default.items()])
        self.__dict__.update(x)

    def update(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        data = {}
        for k, v in self.__dict__.items():
            if v and v != 'null':
                if isinstance(v, (type(ugettext_lazy(' ')))):
                    v = _(v)
                if isinstance(v, (bool)):
                    v = str(v).lower()
                if v == ('null',):
                    v = 'null'
                if unicode(v):
                    data[k] = v
        if not data:
            data = ""
        return unicode(data)

    def create(self, **defaults):
        obj = DictObject(**self.__dict__)
        obj.update(**defaults)
        return obj
