from datetime import datetime
import csv
from dateutil.relativedelta import relativedelta

from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.contrib.contenttypes.models import ContentType
import simplejson
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.core.files.storage import default_storage
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.memberships.models import MembershipDefault
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.payments.models import Payment
from tendenci.apps.base.utils import normalize_newline, tcurrency


def get_user_corp_membership(member_number='', email=''):
    """
    Get corp membership by user member number or email
    """
    from tendenci.apps.corporate_memberships.models import CorpMembership

    if member_number:
        memberships = MembershipDefault.objects.filter(
                                member_number=member_number
                                )
    else:
        memberships = MembershipDefault.objects.filter(
                                user__email=email,
                                corporate_membership_id__gt=0
                                )
    [corp_membership_id] = memberships.values_list('corporate_membership_id',
                                          flat=True)[:1] or [0]
    if corp_membership_id:
        [corp_membership] = CorpMembership.objects.filter(
                        id=corp_membership_id)[:1] or [None]
        return corp_membership
    return None


def get_corpmembership_type_choices(user, corpmembership_app, renew=False, exclude_list=None):
    cmt_list = []
    corporate_membership_types = corpmembership_app.corp_memb_type.all()
    if exclude_list:
        corporate_membership_types = corporate_membership_types.exclude(id__in=exclude_list)

    if not user.profile.is_superuser:
        corporate_membership_types = corporate_membership_types.filter(admin_only=False)
    corporate_membership_types = corporate_membership_types.order_by('position')
    currency_symbol = get_setting("site", "global", "currencysymbol")

    for cmt in corporate_membership_types:
        if not renew:
            price_display = '%s - %s' % (cmt.name, tcurrency(cmt.price))
        else:
            indiv_renewal_price = cmt.membership_type.renewal_price
            if not indiv_renewal_price:
                indiv_renewal_price = '%s<span class="type-ind-price"></span>' % _('Free')
            else:
                indiv_renewal_price = """
                    %s<span class="type-ind-price">%0.2f</span>
                    """ % (currency_symbol, indiv_renewal_price)
            if not cmt.renewal_price:
                cmt.renewal_price = 0
            if cmt.apply_cap:
                indiv_renewal_price = '%s %s %s' % (indiv_renewal_price, _('Limit'), cmt.membership_cap)
                if cmt.allow_above_cap:
                    indiv_renewal_price = '%s - then %s / member' % (indiv_renewal_price,
                                                          tcurrency(cmt.above_cap_price))

            data_cap = '\'{"apply_cap": "%s", "membership_cap":"%s", "allow_above_cap": "%s", "above_cap_price": "%s"}\'' % (
                         cmt.apply_cap, cmt.membership_cap, cmt.allow_above_cap, cmt.above_cap_price)
            price_display = """%s - <b>%s<span class="type-corp-price">%0.2f</span>
                            </b>(individual members:
                            <b>%s</b>)<span class="type-cap" data-cap=%s></span>""" % (cmt.name,
                                            currency_symbol,
                                            cmt.renewal_price,
                                            indiv_renewal_price,
                                            data_cap)
        price_display = mark_safe(price_display)
        cmt_list.append((cmt.id, price_display))

    return cmt_list


def corp_membership_rows(corp_profile_field_names,
                         corp_memb_field_names,
                         foreign_keys):
    from tendenci.apps.corporate_memberships.models import CorpMembership
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
    from tendenci.apps.corporate_memberships.models import CorpMembership
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
    from tendenci.apps.corporate_memberships.models import CorpMembershipAuthDomain
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


def corp_memb_inv_add(user, corp_memb, app=None, **kwargs):
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
                                      model=corp_memb._meta.model_name)
        inv.object_id = corp_memb.id
        inv.title = corp_memb.corp_profile.name

        if not user.is_anonymous():
            inv.bill_to = '%s %s' % (user.first_name, user.last_name)
            inv.bill_to_first_name = user.first_name
            inv.bill_to_last_name = user.last_name
            inv.bill_to_email = user.email
            inv.set_creator(user)
            inv.set_owner(user)
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

        tax = 0
        if app and app.include_tax:
            tax = inv.total * app.tax_rate
            inv.tax = tax
            total = inv.total + tax
            inv.subtotal =total
            inv.total = total
            inv.balance = total

        inv.estimate = True
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
                payment.method = corp_memb.payment_method.machine_name
                payment.save(user)

                # this will make accounting entry
                inv.make_payment(user, payment.amount)
        return inv
    return None


def dues_rep_emails_list(corp_memb):
    from tendenci.apps.corporate_memberships.models import CorpMembershipRep
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
    from tendenci.apps.perms.object_perms import ObjectPermission
    from tendenci.apps.corporate_memberships.models import CorpMembershipRep

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
    from tendenci.apps.corporate_memberships.models import (
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


def get_payment_method_choices(user, corp_app):
    payment_methods = corp_app.payment_methods.all()

    if not user.profile.is_superuser:
        payment_methods = payment_methods.filter(admin_only=False)

    pm_choices = []
    for pm in payment_methods:
        pm_choices.append((pm.pk, pm.human_name))
    return pm_choices


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


def get_over_time_stats():
    """
    return a dict of membership statistics overtime.
    """
    from tendenci.apps.corporate_memberships.models import CorpMembership
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
        active_mems = CorpMembership.objects.filter(expiration_dt__gt=start_dt, status_detail='active')
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
    from tendenci.apps.corporate_memberships.models import CorporateMembershipType, CorpMembership
    now = datetime.now()
    summary = []
    types = CorporateMembershipType.objects.all()
    total_active = 0
    total_pending = 0
    total_expired = 0
    total_total = 0
    for type in types:
        mems = CorpMembership.objects.filter(corporate_membership_type = type)
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


def get_notice_token_help_text(notice=None):
    """Get the help text for how to add the token in the email content,
        and display a list of available token.
    """
    from tendenci.apps.corporate_memberships.models import (
        CorporateMembershipType, CorpMembershipApp, CorpMembershipAppField)
    help_text = ''
    if notice and notice.corporate_membership_type:
        membership_types = [notice.corporate_membership_type]
    else:
        membership_types = CorporateMembershipType.objects.filter(
                                             status=True,
                                             status_detail='active')

    # get a list of apps from membership types
    apps_list = []
    for mt in membership_types:
        apps = CorpMembershipApp.objects.filter(corp_memb_type=mt)
        if apps:
            apps_list.extend(apps)

    apps_list = set(apps_list)
    apps_len = len(apps_list)

    # render the tokens
    help_text += '<div style="margin: 1em 10em;">'
    help_text += """
                <div style="margin-bottom: 1em;">
                You can use tokens to display member info or site specific
                information.
                A token is a field name wrapped in
                {{ }} or [ ]. <br />
                For example, token for name field: {{ name }}.
                </div>
                """

    help_text += '<div id="toggle_token_view"><a href="javascript:;">' + \
                'Click to view available tokens</a></div>'
    help_text += '<div id="notice_token_list">'
    if apps_list:
        for app in apps_list:
            if apps_len > 1:
                help_text += '<div style="font-weight: bold;">%s</div>' % (
                                                            app.name)
            fields = CorpMembershipAppField.objects.filter(
                                        corp_app=app,
                                        display=True,
                                        ).exclude(
                                        field_name=''
                                        ).order_by('position')
            help_text += "<ul>"
            for field in fields:
                help_text += '<li>{{ %s }} - (for %s)</li>' % (
                                                       field.field_name,
                                                       field.label)
            help_text += "</ul>"
    else:
        help_text += '<div>No field tokens because there is no ' + \
                    'applications.</div>'

    other_labels = ['site_contact_name',
                    'site_contact_email',
                    'site_display_name',
                    'time_submitted',
                    'view_link',
                    'renew_link',
                    'rep_first_name',
                    'total_individuals_renewed',
                    'renewed_individuals_list',
                    'invoice_link',
                    'individuals_join_url',
                    'anonymous_join_login_info',
                    'authentication_info'
                    ]
    help_text += '<div style="font-weight: bold;">Non-field Tokens</div>'
    help_text += "<ul>"
    for label in other_labels:
        help_text += '<li>{{ %s }}</li>' % label
    help_text += "</ul>"
    help_text += "</div>"
    help_text += "</div>"

    help_text += """
                <script>
                    $(document).ready(function() {
                        $('#notice_token_list').hide();
                         $('#toggle_token_view').click(function () {
                        $('#notice_token_list').toggle();
                         });
                    });
                </script>
                """

    return help_text


def create_salesforce_lead(sf, corporate_profile):
    [rep] = corporate_profile.reps.all()[:1] or [None]
    if rep:
        name = '%s %s' % (rep.user.first_name, rep.user.last_name)
    else:
        name = corporate_profile.name
    corp_membership = corporate_profile.corp_membership
    if corp_membership:
        Company_Category_c = corp_membership.corporate_membership_type.name
    else:
        Company_Category_c = ''

    if corporate_profile.ud1:
        # Update Salesforce Lead object
        try:
            sf.Lead.update(corporate_profile.ud1, {
                'LastName': name,
                'Company':corporate_profile.name,
                'Company_Category__c': Company_Category_c,
                'Street':'%s %s' %(corporate_profile.address, corporate_profile.address2),
                'City':corporate_profile.city,
                'State':corporate_profile.state,
                'PostalCode':corporate_profile.zip,
                'Country':corporate_profile.country,
                'Phone':corporate_profile.phone,
                'Email':corporate_profile.email,
                'Website':corporate_profile.url})
        except:
            print 'Salesforce lead not found'

    else:
        # Create a new Salesforce Lead object
        result = sf.Lead.create({
            'LastName': name,
            'Company':corporate_profile.name,
            'Company_Category__c': Company_Category_c,
            'Street':'%s %s' %(corporate_profile.address, corporate_profile.address2),
            'City':corporate_profile.city,
            'State':corporate_profile.state,
            'PostalCode':corporate_profile.zip,
            'Country':corporate_profile.country,
            'Phone':corporate_profile.phone,
            'Email':corporate_profile.email,
            'Website':corporate_profile.url})

        corporate_profile.ud1 = result['id']
        corporate_profile.save()
