from datetime import datetime
from tendenci.core.perms.managers import TendenciBaseManager
from tendenci.core.site_settings.utils import get_setting
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

    def released_news_ids(self):
        # use default timezone on settings
        now = localtime_for_timezone(datetime.now(), get_setting('site', 'global', 'defaulttimezone'))
        qset = self.get_query_set()
        return [x.id for x in qset if x.release_dt_with_tz <= now ]

    def released_news(self, qs):
        return qs.filter(id__in=self.released_news_ids())
