import os
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from site_settings.utils import get_setting
from perms.utils import is_admin
from corporate_memberships.models import (CorpField, AuthorizedDomain, CorporateMembershipRep)
from memberships.models import AppField, Membership
from invoices.models import Invoice
from payments.models import Payment


# get the corpapp default fields list from json
def get_corpapp_default_fields_list():
    json_fields_path = os.path.join(settings.PROJECT_ROOT, 
                                    "templates/corporate_memberships/regular_fields.json")
    fd = open(json_fields_path, 'r')
    data = ''.join(fd.read())
    fd.close()
    
    if data:
        return simplejson.loads(data)
    return None

def get_corporate_membership_type_choices(user, corpapp, renew=False):
    cmt_list = []
    corporate_membership_types = corpapp.corp_memb_type.all()
    
    if not is_admin(user):
        corporate_membership_types = corporate_membership_types.filter(admin_only=False)
    currency_symbol = get_setting("site", "global", "currencysymbol")
    
    for cmt in corporate_membership_types:
        if not renew:
            price_display = '%s - %s%0.2f' % (cmt.name, currency_symbol, cmt.price)
        else:
            indiv_renewal_price = cmt.membership_type.renewal_price
            if not indiv_renewal_price:
                indiv_renewal_price = 'Free<span class="type-ind-price"></span>'
            else:
                indiv_renewal_price = '%s<span class="type-ind-price">%0.2f</span>' % (currency_symbol, indiv_renewal_price)
            if not cmt.renewal_price:
                cmt.renewal_price = 0
            
            price_display = """%s - <b>%s<span class="type-corp-price">%0.2f</span></b> 
                            (individual members renewal: 
                            <b>%s</b>)""" % (cmt.name, 
                                            currency_symbol, 
                                            cmt.renewal_price,
                                            indiv_renewal_price)
        price_display = mark_safe(price_display)
        cmt_list.append((cmt.id, price_display))
            
    return cmt_list 

def get_indiv_membs_choices(corp):
    im_list = []
    indiv_memberships = Membership.objects.filter(corporate_membership_id=corp.id)
    
    for membership in indiv_memberships:
        indiv_memb_display = '<a href="%s" target="_blank">%s</a>' % (reverse('profile', args=[membership.user.username]), 
                                                                      membership.user.get_full_name())
        indiv_memb_display = mark_safe(indiv_memb_display)
        im_list.append((membership.id, indiv_memb_display))
    
    return im_list        
   
def get_payment_method_choices(user):
    if is_admin(user):
        return (('paid - check', 'User paid by check'),
                ('paid - cc', 'User paid by credit card'),
                ('Credit Card', 'Make online payment NOW'),)
    else:
        return (('check', 'Check'),
                ('cash', 'Cash'),
                ('cc', 'Credit Card'),)
    
        
def corp_memb_inv_add(user, corp_memb, **kwargs): 
    """
    Add an invoice for this corporate membership
    """
    renewal = kwargs.get('renewal', False)
    renewal_total = kwargs.get('renewal_total', 0)
    renew_entry = kwargs.get('renew_entry', None)
    if not corp_memb.invoice or renewal:
        inv = Invoice()
        if renew_entry:
            inv.object_type = ContentType.objects.get(app_label=renew_entry._meta.app_label, 
                                                      model=renew_entry._meta.module_name)
            inv.object_id = renew_entry.id
        else:
            inv.object_type = ContentType.objects.get(app_label=corp_memb._meta.app_label, 
                                                      model=corp_memb._meta.module_name)
            inv.object_id = corp_memb.id
        inv.title = "Corporate Membership Invoice"
        inv.bill_to = corp_memb.name
        inv.bill_to_company = corp_memb.name
        inv.bill_to_address = corp_memb.address
        inv.bill_to_city = corp_memb.city
        inv.bill_to_state = corp_memb.state
        inv.bill_to_zip_code = corp_memb.zip
        inv.bill_to_country = corp_memb.country
        inv.bill_to_phone = corp_memb.phone
        inv.bill_to_email = corp_memb.email
        inv.ship_to = corp_memb.name
        inv.ship_to_company = corp_memb.name
        inv.ship_to_address = corp_memb.address
        inv.ship_to_city = corp_memb.city
        inv.ship_to_state = corp_memb.state
        inv.ship_to_zip_code = corp_memb.zip
        inv.ship_to_country = corp_memb.country
        inv.ship_to_phone = corp_memb.phone
        inv.ship_to_email =corp_memb.email
        inv.terms = "Due on Receipt"
        inv.due_date = datetime.now()
        inv.ship_date = datetime.now()
        inv.message = 'Thank You.'
        inv.status = True
        
        if not renewal:
            inv.total = corp_memb.corporate_membership_type.price
        else:
            inv.total = renewal_total
        inv.subtotal = inv.total
        inv.balance = inv.total
        inv.estimate = 1
        inv.status_detail = 'estimate'
        inv.save(user)
        
        
        if is_admin(user):
            if corp_memb.payment_method in ['paid - cc', 'paid - check', 'paid - wire transfer']:
                inv.tender(user) 
                
                # payment
                payment = Payment()
                payment.payments_pop_by_invoice_user(user, inv, inv.guid)
                payment.mark_as_paid()
                payment.method = corp_memb.payment_method
                payment.save(user)
                
                # this will make accounting entry
                inv.make_payment(user, payment.amount)
        return inv
    return None
        
def update_auth_domains(corp_memb, domain_names):
    """
    Update the authorized domains for this corporate membership.
    """
    if domain_names:
        dname_list = domain_names.split(',')
        dname_list = [name.strip() for name in dname_list]
        
        # if domain is not in the list domain_names, delete it from db
        # otherwise, remove it from list
        if corp_memb.auth_domains:
            for auth_domain in list(corp_memb.auth_domains.all()):
                if auth_domain.name in dname_list:
                    dname_list.remove(auth_domain.name)
                else:
                    auth_domain.delete()
                    
        # add the rest of the domain
        for name in dname_list:
            auth_domain = AuthorizedDomain(corporate_membership=corp_memb, name=name)
            auth_domain.save()
            
            
        
        
def update_authenticate_fields(corpapp):
    """
        if corpapp.authentication_method == 'admin':
            authorized_domains.required = False
            authorized_domains.visible = False
            secret_code.required = False
            secret_code.visible = False
        elif corpapp.authentication_method == 'email':
            authorized_domains.required = True
            authorized_domains.visible = True
            secret_code.required = False
            secret_code.visible = False
        elif corpapp.authentication_method == 'secret_code':
            authorized_domains.required = False
            authorized_domains.visible = False
            secret_code.required = True
            secret_code.visible = True
    """
    if corpapp:
        authorized_domains = CorpField.objects.get(corp_app=corpapp, field_name='authorized_domains')
        secret_code = CorpField.objects.get(corp_app=corpapp, field_name='secret_code')
        if corpapp.authentication_method == 'admin':
            authorized_domains.required = 0
            authorized_domains.visible = 0
            secret_code.required = 0
            secret_code.visible = 0
        elif corpapp.authentication_method == 'email':
            authorized_domains.required = 1
            authorized_domains.visible = 1
            secret_code.required = 0
            secret_code.visible = 0
        else:   # secret_code
            authorized_domains.required = 0
            authorized_domains.visible = 0
            secret_code.required = 1
            secret_code.visible = 1
            secret_code.no_duplicates = 1
        authorized_domains.save()
        secret_code.save()  
            
def edit_corpapp_update_memb_app(corpapp):
    """
    Update the membership application's corporate membership fields (corporate_membership_id)
    when editing a corporate membership application.
    """
    if corpapp.memb_app:
        app = corpapp.memb_app
        if not app.use_for_corp:
            app.use_for_corp = 1
            app.save()
        try:  
            app_field = AppField.objects.get(app=app, field_type='corporate_membership_id')
        except AppField.DoesNotExist:
            from memberships.utils import get_default_membership_corp_fields
            field_list = get_default_membership_corp_fields()
            for field in field_list:
                field.update({'app':app})
                AppField.objects.create(**field)
                
def dues_rep_emails_list(corp_memb):
    dues_reps = CorporateMembershipRep.objects.filter(corporate_membership=corp_memb,
                                                      is_dues_rep=1)
    return [dues_rep.user.email for dues_rep in dues_reps if dues_rep.user.email]

def corp_memb_update_perms(corp_memb, **kwargs):
    """
    update object permissions to creator, owner and representatives.
    view and change permissions only - no delete permission assigned 
    because we don't want them to delete corporate membership records.
    """
    from perms.object_perms import ObjectPermission
    
    ObjectPermission.objects.remove_all(corp_memb)
    
    perms = ['view', 'change']
    
    # creator and owner
    if corp_memb.creator:
        ObjectPermission.objects.assign(corp_memb.creator, corp_memb, perms=perms)
        
    if corp_memb.owner:
        ObjectPermission.objects.assign(corp_memb.owner, corp_memb, perms=perms)
        
    # dues and members reps
    reps = CorporateMembershipRep.objects.filter(corporate_membership=corp_memb)
    for rep in reps:
        ObjectPermission.objects.assign(rep.user, corp_memb, perms=perms)
        
    return corp_memb
    

            
            
        
               
    