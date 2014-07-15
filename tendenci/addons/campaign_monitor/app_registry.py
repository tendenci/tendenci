from tendenci.core.registry import site
from tendenci.core.registry.base import CoreRegistry, lazy_reverse
from tendenci.addons.campaign_monitor.models import Template, Campaign


# class TemplateRegistry(CoreRegistry):
#     version = '1.0'
#     author = 'Schipul - The Web Marketing Company'
#     author_email = 'programmers@schipul.com'
#     description = 'Create templates via the Campaign Monitor API'
#
#     url = {
#         'add': lazy_reverse('campaign_monitor.template_add'),
#         'search': lazy_reverse('campaign_monitor.template_index'),
#     }
#
# class CampaignRegistry(CoreRegistry):
#     version = '1.0'
#     author = 'Schipul - The Web Marketing Company'
#     author_email = 'programmers@schipul.com'
#     description = 'Create campaigns via the Campaign Monitor API'
#
#     url = {
#         'add': lazy_reverse('campaign_monitor.campaign_add'),
#         'search': lazy_reverse('campaign_monitor.campaign_index'),
#     }
#
# site.register(Template, TemplateRegistry)
# site.register(Campaign, CampaignRegistry)
