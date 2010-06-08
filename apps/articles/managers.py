from django.db.models import Manager

from haystack.query import SearchQuerySet

class ArticleManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query articles. 
            Returns a SearchQuerySet
        """
        from articles.models import Article
        sqs = SearchQuerySet()
        
        if query: 
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
        
        return sqs.models(Article)