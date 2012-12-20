from tendenci.core.perms.managers import TendenciBaseManager


class EntityManager(TendenciBaseManager):
    def first(self, **kwargs):
        """
        Returns first instance that matches filters.
        If no instance is found then a none type object is returned.
        """
        [instance] = self.filter(**kwargs).order_by('pk')[:1] or [None]
        return instance
