from django.apps import AppConfig

class RegistryConfig(AppConfig):
    name = 'Registry'
    verbose_name = 'Registry Application'
    
    def ready(self):
        import registry.register
        register.autodiscover()