from tendenci.core.perms.managers import TendenciBaseManager

class PageManager(TendenciBaseManager):
    """
    Model Manager
    """
    def active(self):
        return self.get_query_set().filter(status=1, status_detail='active')