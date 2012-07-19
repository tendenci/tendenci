from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    A management command made to quickly create
    some test data. This will give us a general idea.
    """
    def handle(self, *args, **kwargs):
        from django.contrib.auth.models import User
        from tenants.models import Tenant, Map

        verbosity = int(kwargs['verbosity'])
        user = User.objects.all()[0]
        map = Map.objects.all()[0]
        limit = int(kwargs.get('limit', '3'))

        for i in range(limit):
            tenant = Tenant.objects.create(
                map=map,
                name=u'',
                description=u'test description',
                link=u'http://google.com',
                suite_number=u'4301',
                contact_info=u'some test contact info',
                tags=u'blah1, blah2, blah3',
                creator=user,
                owner=user
            )

            tenant.name = u'Block number %d' % tenant.pk
            tenant.suite_number = u'%d01' % tenant.pk
            tenant.save()

            if verbosity:
                print tenant
