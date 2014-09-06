from tendenci.apps.perms.managers import TendenciBaseManager

class NewsManager(TendenciBaseManager):
    """
    Model Manager
    """

    def search(self, query=None, *args, **kwargs):
        tag_query = "tag:"
        if query and query.startswith(tag_query):
            kwargs['tags-query'] = True

        return super(NewsManager, self).search(query, *args, **kwargs)

