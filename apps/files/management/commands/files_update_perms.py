# from django.core.management.base import BaseCommand

# class Command(BaseCommand):
#     """
#     example: python manage.py 
#     """
#     def handle(self, *args, **kwargs):
#     	from files.models import File

#     	for f in File.objects.all():
#     		if f.is_public:
#     			f.allow_anonymous_view = True
#     			f.save()