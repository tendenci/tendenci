from geraldo import Report, ReportBand, ObjectValue, SystemField,\
    BAND_WIDTH, Label, landscape
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import A5
from datetime import datetime, timedelta

class ReportBandNewMems(ReportBand):
    def __init__(self, *args, **kwargs):
        days_ago = kwargs.pop('days_ago')
        super(ReportBandNewsMems, self).__init__(*args, **kwargs)

class ReportNewMems(Report):
    title = "New Memberships"
    author = "John Smith  Corporation"
    
    page_size = landscape(A5)
    
    def __init__(self, *args, **kwargs):
        super(ReportNewMems, self).__init__(*args, **kwargs)
    
    class band_page_header(ReportBand):
        height = 1.2*cm
        elements = [
                Label(text="Name", top=0.8*cm, left=0*cm),
                Label(text="Email", top=0.8*cm, left=2.5*cm),
                Label(text="Type", top=0.8*cm, left=5.5*cm),
                Label(text="Price Paid", top=0.8*cm, left=11.5*cm),
                Label(text="Start Date", top=0.8*cm, left=14.5*cm),
                Label(text="End Date", top=0.8*cm, left=17.5*cm),
            ]
        
    class band_detail(ReportBand):
        height = 0.5*cm
        elements = (
                ObjectValue(attribute_name='user', left=0*cm,
                    get_value=lambda instance: instance.user.last_name + ', ' + instance.user.first_name),
                ObjectValue(attribute_name='user', left=2.5*cm, 
                    get_value=lambda instance: instance.user.email),
                ObjectValue(attribute_name='membership_type', left=5.5*cm),
                ObjectValue(attribute_name='invoice', left=11.5*cm,
                    get_value=lambda instance: instance.get_invoice().total if instance.get_invoice() else ''),
                #ObjectValue(attribute_name='payment_method', left=15*cm),
                ObjectValue(attribute_name='join_dt', left=14.5*cm,
                    get_value=lambda instance: instance.join_dt.strftime('%b %d, %Y')),
                ObjectValue(attribute_name='expire_dt', left=17.5*cm,
                    get_value=lambda instance: instance.expire_dt.strftime('%b %d, %Y') if instance.expire_dt else ''),
            )
    
