from datetime import datetime
from tendenci.core.perms.managers import TendenciBaseManager
from timezones.utils import localtime_for_timezone

class NewsManager(TendenciBaseManager):
    """
    Model Manager
    """

    def search(self, query=None, *args, **kwargs):
        tag_query = "tag:"
        if query and query.startswith(tag_query):
            kwargs['tags-query'] = True

        return super(NewsManager, self).search(query, *args, **kwargs)

    def released_news(self):
        # use default timezone on settings
        now = localtime_for_timezone(datetime.now(), None)
        qset = self.get_query_set()
        ids = [x.id for x in qset if x.release_dt_default_tz <= now ]
        return qset.filter(id__in=ids)
