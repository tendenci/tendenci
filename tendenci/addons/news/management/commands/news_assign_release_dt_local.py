from django.core.management.base import BaseCommand


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        from tendenci.addons.news.models import News
        
        news = News.objects.all()
        for n in news:
            if not n.release_dt_local:
                n.assign_release_dt_local()
                News.objects.filter(id=n.id).update(release_dt_local=n.release_dt_local)