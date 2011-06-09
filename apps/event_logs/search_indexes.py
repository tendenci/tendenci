from haystack import indexes
from haystack import site
from event_logs.models import EventLog


class EventLogIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    create_dt = indexes.DateTimeField(model_attr='create_dt')

    content_type = indexes.CharField(model_attr='content_type', null=True)
    source = indexes.CharField(model_attr='source', null=True)
    entity = indexes.CharField(model_attr='entity', null=True)
    event_id = indexes.IntegerField(model_attr='event_id')
    event_name = indexes.CharField(model_attr='event_name')
    event_type = indexes.CharField(model_attr='event_type')
    event_data = indexes.CharField(model_attr='event_data')
    category = indexes.CharField(model_attr='category', null=True)
    session_id = indexes.CharField(model_attr='session_id', null=True)
    user = indexes.CharField(model_attr='user', null=True)
    username = indexes.CharField(model_attr='username', null=True)
    email = indexes.CharField(model_attr='email', null=True)
    user_ip_address = indexes.CharField(model_attr='user_ip_address', null=True)
    server_ip_address = indexes.CharField(model_attr='server_ip_address', null=True)
    url = indexes.CharField(model_attr='url', null=True)
    http_referrer = indexes.CharField(model_attr='http_referrer', null=True)
    headline = indexes.CharField(model_attr='headline', null=True)
    description = indexes.CharField(model_attr='description', null=True)
    http_user_agent = indexes.CharField(model_attr='http_user_agent', null=True)
    request_method = indexes.CharField(model_attr='request_method', null=True)
    query_string = indexes.CharField(model_attr='query_string', null=True)
    robot = indexes.CharField(model_attr='robot', null=True)
    create_dt = indexes.DateTimeField(model_attr='create_dt')

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    def get_updated_field(self):
        return 'create_dt'

site.register(EventLog, EventLogIndex)
