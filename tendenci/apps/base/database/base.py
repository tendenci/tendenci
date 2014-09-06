from django.db.backends.postgresql_psycopg2.base import *

class DatabaseOperations(DatabaseOperations):
    def lookup_cast(self, lookup_type):
        if lookup_type in('icontains', 'istartswith'):
            return "UPPER(unaccent(%s::text))"
        else:
            return super(DatabaseOperations, self).lookup_cast(lookup_type)

class DatabaseWrapper(DatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.operators['icontains'] = 'LIKE UPPER(unaccent(%s))'
        self.operators['istartswith'] = 'LIKE UPPER(unaccent(%s))'
        self.ops = DatabaseOperations(self)