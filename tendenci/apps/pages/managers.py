from tendenci.core.perms.managers import TendenciBaseManager

class PageManager(TendenciBaseManager):
    """
    Model Manager
    """
    def active(self):
        return self.get_query_set().filter(status=True, status_detail='active')