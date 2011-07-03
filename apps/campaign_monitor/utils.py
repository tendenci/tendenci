from createsend import Client
from django.conf import settings

def get_client():
    api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None) 
    client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
    CreateSend.api_key = api_key
    return Client(client_id)
    
def handle_uploaded_file(f):
    destination = open('some/file/name.txt', 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
