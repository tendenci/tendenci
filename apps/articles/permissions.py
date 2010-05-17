from base.auth import BasePermission
from articles.models import Article
from authority import register

class ArticlePermission(BasePermission):
    """
        Permissions for articles
    """
    label = 'article_permission'
    
register(Article, ArticlePermission)