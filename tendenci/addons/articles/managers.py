from tendenci.core.perms.managers import TendenciBaseManager
from tendenci.core.categories.models import Category


class ArticleManager(TendenciBaseManager):
    """
    Model Manager
    """
    def get_categories(self, category=None):
        return Category.objects.get_for_model(self.model, category)
