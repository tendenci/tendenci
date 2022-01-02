from tendenci.apps.perms.managers import TendenciBaseManager

class ChapterManager(TendenciBaseManager):
    """
    Model Manager
    """
    pass


class PositionManager(TendenciBaseManager):
    """
    Model Manager
    """
    pass


class ChapterMembershipTypeManager(TendenciBaseManager):
    pass


class ChapterMembershipManager(TendenciBaseManager):
    pass


class ChapterMembershipAppManager(TendenciBaseManager):
    def current_app(self, **kwargs):
        """
        Returns the app being used currently.
        """
        [current_app] = self.filter(
                           status=True,
                           status_detail__in=['active', 'published']
                           ).order_by('id')[:1] or [None]

        return current_app