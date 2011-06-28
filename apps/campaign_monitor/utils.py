from createsend import Client
from django.conf import settings

def get_client():
    api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None) 
    client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
    CreateSend.api_key = api_key
    return Client(client_id)
    
