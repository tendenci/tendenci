from haystack import indexes
from haystack import site
from invoices.models import Invoice

class InvoiceIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    invoice_object_type = indexes.CharField(model_attr='invoice_object_type')
    invoice_object_type_id = indexes.IntegerField(model_attr='invoice_object_type_id')
    bill_to = indexes.CharField(model_attr='bill_to')
    bill_to_first_name = indexes.CharField(model_attr='bill_to_first_name')
    bill_to_last_name = indexes.CharField(model_attr='bill_to_last_name')
    bill_to_company = indexes.CharField(model_attr='bill_to_company')
    bill_to_address = indexes.CharField(model_attr='bill_to_address')
    bill_to_city = indexes.CharField(model_attr='bill_to_city')
    bill_to_state = indexes.CharField(model_attr='bill_to_state')
    bill_to_zip_code = indexes.CharField(model_attr='bill_to_zip_code')
    bill_to_country = indexes.CharField(model_attr='bill_to_country')
    bill_to_phone = indexes.CharField(model_attr='bill_to_phone')
    bill_to_email = indexes.CharField(model_attr='bill_to_email')
    total = indexes.FloatField(model_attr='total')
    balance = indexes.FloatField(model_attr='balance')
    
    # authority fields
    creator = indexes.CharField(model_attr='creator')
    creator_username = indexes.CharField(model_attr='creator_username')
    owner = indexes.CharField(model_attr='owner')
    owner_username = indexes.CharField(model_attr='owner_username')
    status = indexes.IntegerField(model_attr='status')
    status_detail = indexes.CharField(model_attr='status_detail')
    tender_date = indexes.DateTimeField(model_attr='tender_date')

    
site.register(Invoice, InvoiceIndex)