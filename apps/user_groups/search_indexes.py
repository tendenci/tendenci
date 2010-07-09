from haystack import indexes
from haystack import site
from user_groups.models import Group

class GroupIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    label = indexes.CharField(model_attr='label')
    type = indexes.CharField(model_attr='type')
    description = indexes.CharField(model_attr='description')
   
    # authority fields
    creator = indexes.CharField(model_attr='creator')
    creator_username = indexes.CharField(model_attr='creator_username')
    owner = indexes.CharField(model_attr='owner')
    owner_username = indexes.CharField(model_attr='owner_username')
    status = indexes.IntegerField(model_attr='status')
    status_detail = indexes.CharField(model_attr='status_detail')

    
site.register(Group, GroupIndex)