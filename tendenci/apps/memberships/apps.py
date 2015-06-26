from django.apps import AppConfig

class MembershipsConfig(AppConfig):
    name = 'memberships'
    verbose_name = 'Memberships Application'
    
    def ready(self):
        import memberships.signals