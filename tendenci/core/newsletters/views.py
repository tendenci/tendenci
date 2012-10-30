from django.views.generic import TemplateView
from django.conf import settings


class NewsletterGeneratorView(TemplateView):
    template_name="newsletters/newsletter_generator.html"

    def get_context_data(self, **kwargs):
        context = super(NewsletterGeneratorView, self).get_context_data(**kwargs)
        cm_api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None) 
        cm_client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
        if cm_api_key and cm_client_id:
            context['CAMPAIGNMONITOR_ENABLED'] = True
        else:
            context['CAMPAIGNMONITOR_ENABLED'] = False

        return context