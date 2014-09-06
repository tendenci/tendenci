from django.core.management.base import BaseCommand


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        from tendenci.apps.articles.models import Article
        
        articles = Article.objects.all()
        for art in articles:
            if not art.release_dt_local:
                art.assign_release_dt_local()
                Article.objects.filter(id=art.id).update(release_dt_local=art.release_dt_local)