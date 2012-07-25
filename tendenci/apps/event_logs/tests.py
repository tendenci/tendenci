"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User

from tendenci.apps.event_logs.models import EventLog

class EventLogTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User()
        self.username = 'test_user'
        self.password = 'testing'
        self.email = 'test@testuser.com'
        self.user.save()
        
    def tearDown(self):
        pass
        
    def test_log_no_objects(self):
        """
            Basic event log test with no objects present
            Only pass:
            event_id
            event_data
            description 
        """
        event_log_defaults = {
            'event_id': 111111,
            'event_data': 'Event Data',
            'description': 'unit testing'
        }
        
        self.assertRaises(Exception, EventLog.objects.log(**event_log_defaults))
        

    def test_log_user_object(self):
        """
            Basic event log test with user object
            Only pass:
            event_id
            event_data
            description 
            user
        """
        event_log_defaults = {
            'event_id': 111111,
            'event_data': 'Event Data',
            'description': 'unit testing',
            'user': self.user
        }   
        self.assertRaises(Exception, EventLog.objects.log(**event_log_defaults))
        
    def test_log_request_object(self):
        """
            Basic event log test with request object
            Only pass:
            event_id
            event_data
            description 
            client.response.request
        """
        response = self.client.get('/')
        
        response.request['META'] = {
             'REMOTE_ADDR':'test',
             'HTTP_REFERER':'test',
             'HTTP_USER_AGENT':'test',
             'REQUEST_METHOD':'test',
             'QUERY_STRING':'test'                        
         }
        
        response.request['COOKIE'] = {}
        
        event_log_defaults = {
            'event_id': 111111,
            'event_data': 'Event Data',
            'description': 'unit testing',
            'request': response.request
        }   
        self.assertRaises(Exception, EventLog.objects.log(**event_log_defaults))
    
    def test_log_all(self):
        """
            Basic event log test with all objects
            Only pass:
            event_id
            event_data
            description 
            client.response.request
            user
            instance
        """
        response = self.client.get('/')
        
        response.request['META'] = {
             'REMOTE_ADDR':'test',
             'HTTP_REFERER':'test',
             'HTTP_USER_AGENT':'google',
             'REQUEST_METHOD':'test',
             'QUERY_STRING':'test'                        
         }
        
        response.request['COOKIE'] = {}
        
        event_log_defaults = {
            'event_id': 111111,
            'event_data': 'Event Data',
            'description': 'unit testing',
            'request': response.request,
            'user': self.user,
            'instance': self.user,
        }   
        
        self.assertRaises(Exception, EventLog.objects.log(**event_log_defaults))       
        
            