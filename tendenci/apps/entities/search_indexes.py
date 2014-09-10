#from haystack import indexes
#
#from tendenci.apps.entities.models import Entity
#from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
#
#
#class EntityIndex(TendenciBaseSearchIndex, indexes.Indexable):
#    text = indexes.CharField(document=True, use_template=True)
#    entity_name = indexes.CharField(model_attr='entity_name')
#    entity_type = indexes.CharField(model_attr='entity_type')
#    entity_parent_id = indexes.IntegerField(model_attr='entity_parent_id')
#    contact_name = indexes.CharField(model_attr='contact_name')
#    phone = indexes.CharField(model_attr='phone')
#    fax = indexes.CharField(model_attr='fax')
#    email = indexes.CharField(model_attr='email')
#    website = indexes.CharField(model_attr='website')
#    summary = indexes.CharField(model_attr='summary')
#    notes = indexes.CharField(model_attr='notes')
#    admin_notes = indexes.CharField(model_attr='admin_notes')
#
#
