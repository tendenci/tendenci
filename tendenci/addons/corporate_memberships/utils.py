import os
from datetime import datetime, timedelta
import csv
import dateutil.parser as dparser
from dateutil.relativedelta import relativedelta

from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.core.files.storage import default_storage
from django.utils.translation import ugettext_lazy as _

from tendenci.core.site_settings.utils import get_setting
from tendenci.addons.memberships.models import (AppField,
                                                Membership,
                                                MembershipDefault)
from tendenci.apps.invoices.models import Invoice
from tendenci.core.payments.models import Payment
from tendenci.core.base.utils import normalize_newline


def get_corpmembership_type_choices(user, corpmembership_app, renew=False):
    cmt_list = []
    corporate_membership_types = corpmembership_app.corp_memb_type.all()

    if not user.profile.is_superuser:
        corporate_membership_types = corporate_membership_types.filter(admin_only=False)
    corporate_membership_types = corporate_membership_types.order_by('position')
    currency_symbol = get_setting("site", "global", "currencysymbol")

    for cmt in corporate_membership_types:
        if not renew:
            price_display = '%s - %s%0.2f' % (cmt.name, currency_symbol,
                                              cmt.price)
        else:
            indiv_renewal_price = cmt.membership_type.renewal_price
            if not indiv_renewal_price:
                indiv_renewal_price = 'Free<span class="type-ind-price"></span>'
            else:
                indiv_renewal_price = """
                    %s<span class="type-ind-price">%0.2f</span>
                    """ % (currency_symbol, indiv_renewal_price)
            if not cmt.renewal_price:
                cmt.renewal_price = 0

            price_display = """%s - <b>%s<span class="type-corp-price">%0.2f</span>
                            </b>(individual members:
                            <b>%s</b>)""" % (cmt.name,
                                            currency_symbol,
                                            cmt.renewal_price,
                                            indiv_renewal_price)
        price_display = mark_safe(price_display)
        cmt_list.append((cmt.id, price_display))

    return cmt_list


def corp_membership_rows(corp_profile_field_names,
                         corp_memb_field_names,
                         foreign_keys):
    from tendenci.addons.corporate_memberships.models import CorpMembership
    # grab all except the archived
    corp_memberships = CorpMembership.objects.filter(
                                            status=True
                                ).exclude(
                                status_detail='archive'
                                ).select_related('corp_profile')

    for corp_membership in corp_memberships:
        row_items = []
        corp_profile = corp_membership.corp_profile
        for field_name in corp_profile_field_names:
            if field_name in ['authorized_domains', 'dues_rep']:
                if field_name == 'authorized_domains':
                    auth_domains = corp_profile.authorized_domains.values_list(
                                            'name', flat=True)
                    item = ', '.join(auth_domains)
                if field_name == 'dues_rep':
                    dues_reps = corp_profile.reps.filter(
                                        is_dues_rep=True
                                        ).values_list(
                                            'user__username', flat=True)
                    item = ', '.join(dues_reps)

            else:
                item = getattr(corp_profile, field_name)
                if item and field_name in foreign_keys:
                    # display ids for foreign keys
                    item = item.id
            row_items.append(item)
        for field_name in corp_memb_field_names:
            item = getattr(corp_membership, field_name)
            if item and field_name in foreign_keys:
                item = item.id
            row_items.append(item)

        yield row_items


def get_corp_memberships_choices():
    from tendenci.addons.corporate_memberships.models import CorpMembership
    corp_values = CorpMembership.objects.filter(
                                status=True).exclude(
                                status_detail='archive').values_list(
                                'id', 'corp_profile__name'
                                ).order_by('corp_profile__name')
    corp_list = [(0, _('Select One'))]
    for value in corp_values:
        corp_list.append((value[0], value[1]))

    return corp_list


def get_indiv_memberships_choices(corp_membership):
    im_list = []
    indiv_memberships = MembershipDefault.objects.filter(
                            corp_profile_id=corp_membership.corp_profile.id,
                            status=True).exclude(
                            status_detail='archive'
                                )

    for membership in indiv_memberships:
        indiv_memb_display = '<a href="%s" target="_blank">%s</a>' % (
                                    reverse('profile',
                                            args=[membership.user.username]),
                                        membership.user.get_full_name())
        indiv_memb_display = mark_safe(indiv_memb_display)
        im_list.append((membership.id, indiv_memb_display))

    return im_list


def update_authorized_domains(corp_profile, domain_names):
    """
    Update the authorized domains for this corporate membership.
    """
    from tendenci.addons.corporate_memberships.models import CorpMembershipAuthDomain
    if domain_names.strip():
        dname_list = domain_names.split(',')
        dname_list = [name.strip() for name in dname_list]

        # if domain is not in the list domain_names, delete it from db
        # otherwise, remove it from list
        if corp_profile.authorized_domains:
            for auth_domain in list(corp_profile.authorized_domains.all()):
                if auth_domain.name in dname_list:
                    dname_list.remove(auth_domain.name)
                else:
                    auth_domain.delete()

        # add the rest of the domain
        for name in dname_list:
            auth_domain = CorpMembershipAuthDomain(corp_profile=corp_profile,
                                                   name=name)
            auth_domain.save()


def corp_memb_inv_add(user, corp_memb, **kwargs):
    """
    Add an invoice for this corporate membership
    """
    corp_profile = corp_memb.corp_profile
    renewal = kwargs.get('renewal', False)
    renewal_total = kwargs.get('renewal_total', 0)
    if not corp_memb.invoice or renewal:
        inv = Invoice()
        inv.object_type = ContentType.objects.get(
                                      app_label=corp_memb._meta.app_label,
                                      model=corp_memb._meta.module_name)
        inv.object_id = corp_memb.id
        inv.title = "Corporate Membership Invoice"
        if not user.is_anonymous():
            inv.bill_to = '%s %s' % (user.first_name, user.last_name)
            inv.bill_to_first_name = user.first_name
            inv.bill_to_last_name = user.last_name
            inv.bill_to_email = user.email
        else:
            if corp_memb.anonymous_creator:
                cmc = corp_memb.anonymous_creator
                inv.bill_to = '%s %s' % (cmc.first_name, cmc.last_name)
                inv.bill_to_first_name = cmc.first_name
                inv.bill_to_last_name = cmc.last_name
                inv.bill_to_email = cmc.email
            else:
                inv.bill_to = corp_memb.name

        inv.bill_to_company = corp_profile.name
        inv.bill_to_address = corp_profile.address
        inv.bill_to_city = corp_profile.city
        inv.bill_to_state = corp_profile.state
        inv.bill_to_zip_code = corp_profile.zip
        inv.bill_to_country = corp_profile.country
        inv.bill_to_phone = corp_profile.phone
        inv.ship_to = corp_profile.name
        inv.ship_to_company = corp_profile.name
        inv.ship_to_address = corp_profile.address
        inv.ship_to_city = corp_profile.city
        inv.ship_to_state = corp_profile.state
        inv.ship_to_zip_code = corp_profile.zip
        inv.ship_to_country = corp_profile.country
        inv.ship_to_phone = corp_profile.phone
        inv.ship_to_email = corp_profile.email
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

        if not corp_memb.payment_method:
            is_online = True
            if inv.balance <= 0:
                is_online = False
            corp_memb.payment_method = corp_memb.get_payment_method(
                                            is_online=is_online)

        if user.profile.is_superuser:
            # if offline payment method
            if not corp_memb.payment_method.is_online:
                inv.tender(user)  # tendered the invoice for admin if offline

                # mark payment as made
                payment = Payment()
                payment.payments_pop_by_invoice_user(user, inv, inv.guid)
                payment.mark_as_paid()
                payment.method = corp_memb.get_payment_method()
                payment.save(user)

                # this will make accounting entry
                inv.make_payment(user, payment.amount)
        return inv
    return None


def dues_rep_emails_list(corp_memb):
    from tendenci.addons.corporate_memberships.models import CorpMembershipRep
    dues_reps = CorpMembershipRep.objects.filter(
                                corp_profile=corp_memb.corp_profile,
                                is_dues_rep=True)
    if dues_reps:
        return [dues_rep.user.email \
                for dues_rep in dues_reps \
                if dues_rep.user.email]
    return []


def corp_membership_update_perms(corp_memb, **kwargs):
    """
    update object permissions to creator, owner and representatives.
    view and change permissions only - no delete permission assigned 
    because we don't want them to delete corp membership records.
    """
    from tendenci.core.perms.object_perms import ObjectPermission
    from tendenci.addons.corporate_memberships.models import CorpMembershipRep

    ObjectPermission.objects.remove_all(corp_memb)

    perms = ['view', 'change']

    # creator and owner
    if corp_memb.creator:
        ObjectPermission.objects.assign(corp_memb.creator, corp_memb, perms=perms)

    if corp_memb.owner:
        ObjectPermission.objects.assign(corp_memb.owner, corp_memb, perms=perms)

    # dues and members reps
    reps = CorpMembershipRep.objects.filter(corp_profile=corp_memb.corp_profile)
    for rep in reps:
        ObjectPermission.objects.assign(rep.user, corp_memb, perms=perms)

    return corp_memb


def get_corp_memb_summary():
    from tendenci.addons.corporate_memberships.models import (
                                        CorporateMembershipType,
                                        CorpMembership)
    summary = []
    corp_memb_types = CorporateMembershipType.objects.all()
    total_active = 0
    total_pending = 0
    total_expired = 0
    total_in_grace_period = 0
    total_total = 0
    for corp_memb_type in corp_memb_types:
        membership_type = corp_memb_type.membership_type
        grace_period = membership_type.expiration_grace_period
        now = datetime.now()
        date_to_expire = now - relativedelta(days=grace_period)
        mems = CorpMembership.objects.filter(
                    corporate_membership_type=corp_memb_type)
        active = mems.filter(status=True, status_detail='active',
                             expiration_dt__gt=now
                             )
        expired = mems.filter(status=True,
                              status_detail__in=('expired', 'active'),
                              expiration_dt__lt=date_to_expire)
        in_grace_period = mems.filter(status=True,
                              status_detail='active',
                              expiration_dt__lte=now,
                              expiration_dt__gt=date_to_expire)
        pending = mems.filter(status=True, status_detail__contains='ending')

        active_count = active.count()
        pend_count = pending.count()
        expired_count = expired.count()
        in_grace_period_count = in_grace_period.count()
        type_total = sum([active_count,
                            pend_count,
                            expired_count,
                            in_grace_period_count
                            ])

        total_active += active_count
        total_pending += pend_count
        total_expired += expired_count
        total_in_grace_period += in_grace_period_count
        total_total += type_total
        summary.append({
            'type': corp_memb_type,
            'active': active_count,
            'pending': pend_count,
            'expired': expired_count,
            'in_grace_period': in_grace_period_count,
            'total': type_total,
        })

    return (sorted(summary, key=lambda x: x['type'].name),
        {'total_active': total_active,
         'total_pending': total_pending,
         'total_expired': total_expired,
         'total_in_grace_period': total_in_grace_period,
         'total_total': total_total})


# get the corpapp default fields list from json
def get_corpapp_default_fields_list():
#    json_fields_path = os.path.join(settings.PROJECT_ROOT, 
#                                    "templates/corporate_memberships/regular_fields.json")
#    fd = open(json_fields_path, 'r')
#    data = ''.join(fd.read())
#    fd.close()
    
    data = render_to_string('corporate_memberships/regular_fields.json', 
                               {}, context_instance=None)
    
    if data:
        return simplejson.loads(data)
    return None


def get_corporate_membership_type_choices(user, corpapp, renew=False):
    cmt_list = []
    corporate_membership_types = corpapp.corp_memb_type.all()
    
    if not user.profile.is_superuser:
        corporate_membership_types = corporate_membership_types.filter(admin_only=False)
    corporate_membership_types = corporate_membership_types.order_by('position')
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
    indiv_memberships = Membership.objects.filter(
                            corporate_membership_id=corp.id,
                            status_detail__in=['active', 'expired'],
                            status=True)

    for membership in indiv_memberships:
        indiv_memb_display = '<a href="%s" target="_blank">%s</a>' % (reverse('profile', args=[membership.user.username]), 
                                                                      membership.user.get_full_name())
        indiv_memb_display = mark_safe(indiv_memb_display)
        im_list.append((membership.id, indiv_memb_display))
    
    return im_list        
   

def get_payment_method_choices(user, corp_app):
    payment_methods = corp_app.payment_methods.all()
    
    if not user.profile.is_superuser:
        payment_methods = payment_methods.filter(admin_only=False)
    
    pm_choices = []    
    for pm in payment_methods:
        pm_choices.append((pm.pk, pm.human_name))
    return pm_choices


def update_auth_domains(corp_memb, domain_names):
    """
    Update the authorized domains for this corporate membership.
    """
    from tendenci.addons.corporate_memberships.models import AuthorizedDomain
    
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
            secret_code.required = False
            secret_code.visible = False
            # the secret_code will be auto-generated by the system
    """
    from tendenci.addons.corporate_memberships.models import CorpField
    if corpapp:
        authorized_domains = CorpField.objects.get(corp_app=corpapp, field_name='authorized_domains')
        #secret_code = CorpField.objects.get(corp_app=corpapp, field_name='secret_code')
        if corpapp.authentication_method == 'admin':
            authorized_domains.required = 0
            authorized_domains.visible = 0
            #secret_code.required = 0
            #secret_code.visible = 0
        elif corpapp.authentication_method == 'email':
            authorized_domains.required = 1
            authorized_domains.visible = 1
            #secret_code.required = 0
            #secret_code.visible = 0
        else:   # secret_code
            authorized_domains.required = 0
            authorized_domains.visible = 0
            #secret_code.required = 0
            #secret_code.visible = 0
            #secret_code.no_duplicates = 1
            
        authorized_domains.save(force_update=True)
        #secret_code.save(force_update=True)
            
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
            from tendenci.addons.memberships.utils import get_default_membership_corp_fields
            field_list = get_default_membership_corp_fields()
            for field in field_list:
                field.update({'app':app})
                AppField.objects.create(**field)


def corp_memb_update_perms(corp_memb, **kwargs):
    """
    update object permissions to creator, owner and representatives.
    view and change permissions only - no delete permission assigned 
    because we don't want them to delete corporate membership records.
    """
    from tendenci.core.perms.object_perms import ObjectPermission
    from tendenci.addons.corporate_memberships.models import CorporateMembershipRep
    
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
  
  
def csv_to_dict(file_path):
    data_list = []
    
    data = csv.reader(default_storage.open(file_path, 'rU'))
    fields = data.next()

    fields = [smart_str(field) for field in fields]

    for row in data:
        item = dict(zip(fields, row))
        data_list.append(item)
    return data_list

def validate_import_file(file_path):
    """
    Run import file against required fields
    'name' and 'corporate_membership_type' are required fields
    """
    normalize_newline(file_path)
    data = csv.reader(default_storage.open(file_path, mode='rU'))
    fields = data.next()
    fields = [smart_str(field) for field in fields]

    corp_memb_keys = [slugify(cm) for cm in fields]
    required = ('name','corporate_membership_type')
    requirements = [r in corp_memb_keys for r in required]
    missing_required_fields = [r for r in required if r not in fields]

    return all(requirements), missing_required_fields

def new_corp_mems_from_csv(request, file_path, corp_app, columns, update_option='skip'):
    """
    Create corporatemembership objects (not in database)
    CorporateMembership objects are based on the import csv file
    An extra field called columns can be passed in for field mapping
    A corporate membership application is required
    """
    from tendenci.addons.corporate_memberships.models import CorporateMembershipType, CorporateMembership
    corp_memb_dicts = []
    for csv_dict in csv_to_dict(file_path):  # field mapping
        corp_memb_dict = {}
        for native_column, foreign_column in columns.items():
            if foreign_column: # skip if column not selected
                corp_memb_dict[native_column] = csv_dict[foreign_column]

        corp_memb_dicts.append(corp_memb_dict)

    corp_memb_set = []
    corp_memb_field_names = [smart_str(field.name) for field in CorporateMembership._meta.fields]
    corp_memb_field_types =  [field.__class__.__name__ for field in CorporateMembership._meta.fields]
    corp_memb_field_type_dict = dict(zip(corp_memb_field_names, corp_memb_field_types))

    processed_names = []
    for cm in corp_memb_dicts:
        is_valid = True
        err_msg = ''
        
        try:
            name = cm['name']
        except:
            name = None
            is_valid = False
            err_msg = "Name is blank"
            
        if name in processed_names:
            err_msg = 'Duplicates - the record with the same name "%s" already exists.' % name
            is_valid = False
        else:
            processed_names.append(name)
            
        if is_valid:
            try:
                corp_memb = CorporateMembership.objects.get(name=name)
            except CorporateMembership.DoesNotExist:
                    corp_memb = CorporateMembership(
                        name=name,
                        creator=request.user,
                        creator_username=request.user.username,
                        owner=request.user,
                        owner_username=request.user.username
                    )
        else:
            corp_memb = CorporateMembership(name=name)

        corp_memb.is_valid = is_valid
        corp_memb.err_msg = err_msg

        try:  # if membership type exists
            corp_memb_type = CorporateMembershipType.objects.get(name=cm['corporate_membership_type'])
            corp_memb.corporate_membership_type = corp_memb_type
        except:
            corp_memb_type  = None
            corp_memb.is_valid = False
            corp_memb.err_msg += "Corporate membership type '%s' does not exist." % cm.get('corporate_membership_type')

        corp_memb.cm = cm

        if (not corp_memb.is_valid) or (corp_memb.pk and update_option=='skip'):
            corp_memb_set.append(corp_memb)
            continue    # stop processing if not valid 
                        # or if 'skip' is the update option and the record exists

        # for each field in the corporate membership, assign the value accordingly
        for field_name in corp_memb_field_names:
            if cm.has_key(field_name):
                if corp_memb_field_type_dict[field_name] == 'DateTimeField':

                    # if (empty cell) and (field in renew_dt, expiration_dt)
                    if (not cm[field_name]) and field_name in ['renew_dt', 'expiration_dt']:
                        pass # skip for 'join_dt', 'expiration_dt' - we don't want to auto-assign today's date
                    else:
                        try:
                            # maybe need to skip the expiration_dt if expiration_dt is None
                            tm = (dparser.parse(cm[field_name])).timetuple() 
                            cm[field_name] = datetime(tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec)
                        except:
                            pass

                if corp_memb_field_type_dict[field_name] == 'BooleanField':
                    cm[field_name] = bool(cm[field_name])
                if corp_memb_field_type_dict[field_name] == 'IntegerField':
                    try:
                        cm[field_name] = int(cm[field_name])
                    except:
                        cm[field_name] = 0
                        
                if corp_memb.pk:      
                    old_value = getattr(corp_memb, field_name)
                else:
                    old_value = None
                
                if corp_memb.pk and update_option == 'update' and old_value:
                    # this is an existing record but the field is not blank 
                    pass
                else:
                    try:
                        setattr(corp_memb, field_name, cm[field_name])
                    except ValueError:
                        pass
            else:
                if corp_memb_field_type_dict[field_name] == 'CharField':
                    setattr(corp_memb, field_name, unicode())

        if corp_memb.renew_dt:
            if not corp_memb.renewal:
                corp_memb.renewal = 1
        else:
            corp_memb.renew_dt = None
            corp_memb.renewal = 0
                
        if not corp_memb.join_dt:
            corp_memb.join_dt = datetime.now()

        corp_memb.expiration_dt = cm.get('expiration_dt')

        if not corp_memb.expiration_dt:
            corp_memb.expiration_dt = corp_memb_type.get_expiration_dt(
                join_dt=corp_memb.join_dt,
                renew_dt=corp_memb.renew_dt,
                renewal=corp_memb.renewal
            )

        if not corp_memb.pk:
            corp_memb.corp_app = corp_app 
            corp_memb.status = bool(cm.get('status', True))
            corp_memb.status_detail = cm.get('status-detail', 'active')
  
        if not corp_memb.secret_code:
            corp_memb.assign_secret_code()

        corp_memb_set.append(corp_memb)
        
    return corp_memb_set

def get_over_time_stats():
    """
    return a dict of membership statistics overtime.
    """
    from tendenci.addons.corporate_memberships.models import CorporateMembership
    now = datetime.now()
    this_month = datetime(day=1, month=now.month, year=now.year)
    this_year = datetime(day=1, month=1, year=now.year)
    times = [
        ("Month", this_month, 0),
        ("Last Month", last_n_month(1), 1),
        ("Last 3 Months", last_n_month(2), 2),
        ("Last 6 Months", last_n_month(5), 3),
        ("Year", this_year, 4),
    ]
    
    stats = []
    
    for time in times:
        start_dt = time[1]
        d = {}
        active_mems = CorporateMembership.objects.filter(expiration_dt__gt=start_dt, status_detail='active')
        d['new'] = active_mems.filter(join_dt__gt=start_dt).count() #just joined in that time period
        d['renewing'] = active_mems.filter(renewal=True).count()
        d['active'] = active_mems.count()
        d['time'] = time[0]
        d['start_dt'] = start_dt
        d['end_dt'] = now
        d['order'] = time[2]
        stats.append(d)
    
    return sorted(stats, key=lambda x:x['order'])

def get_summary():
    from tendenci.addons.corporate_memberships.models import CorporateMembershipType, CorporateMembership
    now = datetime.now()
    summary = []
    types = CorporateMembershipType.objects.all()
    total_active = 0
    total_pending = 0
    total_expired = 0
    total_total = 0
    for type in types:
        mems = CorporateMembership.objects.filter(corporate_membership_type = type)
        active = mems.filter(status_detail='active')
        expired = mems.filter(status_detail='expired')
        pending = mems.filter(status_detail__contains='ending')
        total_active += active.count()
        total_pending += pending.count()
        total_expired += expired.count()
        total_total += mems.count()
        summary.append({
            'type':type,
            'active':active.count(),
            'pending':pending.count(),
            'expired':expired.count(),
            'total':mems.count(),
        })
    
    return (sorted(summary, key=lambda x:x['type'].name),
        (total_active, total_pending, total_expired, total_total))

def last_n_month(n):
    """
        Get the first day of the last n months.
    """
    now = datetime.now()
    last = now - relativedelta(months=n)
    return datetime(day=1, month=last.month, year=last.year)
