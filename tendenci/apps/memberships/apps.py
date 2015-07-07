from django.apps import AppConfig

class MembershipsConfig(AppConfig):
    name = 'tendenci.apps.memberships'
    verbose_name = 'Memberships Application'
    
    def ready(self):
        super(MembershipsConfig, self).ready()
        import tendenci.apps.memberships.signals