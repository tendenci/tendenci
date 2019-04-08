# settings - directoriespaymenttypes, directoriesrequirespayment
from datetime import datetime, date, time
from io import BytesIO
from PIL import Image
import time as ttime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from django.urls import reverse
from django.db.models.fields import AutoField
from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.utils.translation import gettext

from tendenci.apps.directories.models import Directory, DirectoryPricing
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.base.utils import UnicodeWriter
from tendenci.apps.emails.models import Email
from tendenci.apps.payments.models import Payment
from tendenci.apps.site_settings.utils import get_setting
from tendenci.libs.storage import get_default_storage


def resize_s3_image(image_path, width=200, height=200):
    """
    Resize an image on s3.
    The image_path is the relative path to the media storage.
    """
    storage = get_default_storage()
    f = storage.open(image_path)
    content = f.read()
    f.close()
    img = Image.open(BytesIO(content))
    img.thumbnail((width,height),Image.ANTIALIAS)
    f = storage.open(image_path, 'w')
    img.save(f)
    f.close()

def get_duration_choices(user):
    currency_symbol = get_setting('site', 'global', 'currencysymbol')
    pricings = DirectoryPricing.objects.filter(status=True).order_by('duration')
    choices = []
    for pricing in pricings:
        if pricing.duration == 0:
            if user.profile.is_superuser:
                choice = (pricing.pk, 'Unlimited')
            else:
                continue
        else:
            if pricing.show_member_pricing and user.profile.is_member:
                prices = "%s%s(R)/%s(P)" % (currency_symbol,pricing.regular_price_member,
                                            pricing.premium_price_member)
            else:
                prices = "%s%s(R)/%s(P)" % (currency_symbol, pricing.regular_price,
                                    pricing.premium_price)
            choice = (pricing.pk, '%d days for %s' % (pricing.duration, prices))
        choices.append(choice)

    return choices

def get_payment_method_choices(user):
    if user.profile.is_superuser:
        return (('paid - check', gettext('User paid by check')),
                ('paid - cc', gettext('User paid by credit card')),
                ('Credit Card', gettext('Make online payment NOW')),)
    else:
        directory_payment_types = get_setting('module', 'directories', 'directoriespaymenttypes')
        if directory_payment_types:
            directory_payment_types_list = directory_payment_types.split(',')
            directory_payment_types_list = [item.strip() for item in directory_payment_types_list]

            return [(item, item) for item in directory_payment_types_list]
        else:
            return ()

def directory_set_inv_payment(user, directory, pricing):
    if get_setting('module', 'directories', 'directoriesrequirespayment'):
        if not directory.invoice:
            inv = Invoice()
            inv.object_type = ContentType.objects.get(app_label=directory._meta.app_label,
                                              model=directory._meta.model_name)
            inv.object_id = directory.id
            inv.title = "Directory Add Invoice"
            inv.bill_to_user(user)
            inv.ship_to_user(user)

            inv.terms = "Due on Receipt"
            inv.due_date = datetime.now()
            inv.ship_date = datetime.now()
            inv.message = 'Thank You.'
            inv.status = True

            inv.total = get_directory_price(user, directory, pricing)
            inv.subtotal = inv.total
            inv.balance = inv.total
            inv.estimate = True
            inv.status_detail = 'estimate'

            if user and not user.is_anonymous:
                inv.set_creator(user)
                inv.set_owner(user)

            inv.save(user)

            # tender the invoice
            inv.tender(user)

            # update job
            directory.invoice = inv
            directory.save()

            if user.profile.is_superuser:
                if directory.payment_method in ['paid - cc', 'paid - check', 'paid - wire transfer']:
                    inv.tender(user)

                    # payment
                    payment = Payment()
                    payment.payments_pop_by_invoice_user(user, inv, inv.guid)
                    payment.mark_as_paid()
                    payment.method = directory.payment_method
                    payment.save(user)

                    # this will make accounting entry
                    inv.make_payment(user, payment.amount)


def get_directory_price(user, directory, pricing):
    return pricing.get_price_for_user(
                      user=user,
                      list_type=directory.list_type)


def is_free_listing(user, pricing_id, list_type):
    """
    Check if a directory listing with the specified pricing and list type is free.
    """
    try:
        pricing_id = int(pricing_id)
    except:
        pricing_id = 0
    [pricing] = pricing_id and DirectoryPricing.objects.filter(pk=pricing_id)[:1] or [None]

    if pricing:
        return pricing.get_price_for_user(user, list_type=list_type) <= 0
    return False


def process_export(export_fields='all_fields', export_status_detail='',
                   identifier=u'', user_id=0):
    from tendenci.apps.perms.models import TendenciBaseModel

    if export_fields == 'main_fields':
        field_list = [
            'headline',
            'slug',
            'summary',
            'body',
            'source',
            'first_name',
            'last_name',
            'address',
            'address2',
            'city',
            'state',
            'zip_code',
            'country',
            'phone',
            'phone2',
            'fax',
            'email',
            'email2',
            'website',
            'list_type',
            'requested_duration',
            'activation_dt',
            'expiration_dt',
            'tags',
            'enclosure_url',
            'enclosure_type',
            'enclosure_length',
            'status',
            'status_detail']
    else:
        # base ------------
        base_field_list = [
            smart_str(field.name) for field in TendenciBaseModel._meta.fields
            if not field.__class__ == AutoField]

        field_list = [
            smart_str(field.name) for field in Directory._meta.fields
            if not field.__class__ == AutoField]
        field_list = [
            name for name in field_list
            if name not in base_field_list]
        field_list.remove('guid')
        # append base fields at the end
        field_list = field_list + base_field_list

    identifier = identifier or int(ttime.time())
    file_name_temp = 'export/directories/%s_temp.csv' % identifier

    with default_storage.open(file_name_temp, 'wb') as csvfile:
        csv_writer = UnicodeWriter(csvfile, encoding='utf-8')
        fields_names = list(field_list)
        for i, item in enumerate(fields_names):
            if item == 'headline':
                fields_names[i] = 'name'
            if item == 'body':
                fields_names[i] = 'description'
        csv_writer.writerow(fields_names)

        directories = Directory.objects.all()
        if export_status_detail:
            directories = directories.filter(status_detail__icontains=export_status_detail)
        for directory in directories:
            items_list = []
            for field_name in field_list:
                item = getattr(directory, field_name)
                if item is None:
                    item = ''
                if item:
                    if isinstance(item, datetime):
                        item = item.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(item, date):
                        item = item.strftime('%Y-%m-%d')
                    elif isinstance(item, time):
                        item = item.strftime('%H:%M:%S')
                    elif field_name == 'invoice':
                        # display total vs balance
                        item = 'Total: %d / Balance: %d' % (item.total, item.balance)
                items_list.append(item)
            csv_writer.writerow(items_list)

    # rename the file name
    file_name = 'export/directories/%s.csv' % identifier
    default_storage.save(file_name, default_storage.open(file_name_temp, 'rb'))

    # delete the temp file
    default_storage.delete(file_name_temp)

    # notify user that export is ready to download
    [user] = User.objects.filter(pk=user_id)[:1] or [None]
    if user and user.email:
        download_url = reverse('directory.export_download', args=[identifier])

        site_url = get_setting('site', 'global', 'siteurl')
        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        parms = {
            'download_url': download_url,
            'user': user,
            'site_url': site_url,
            'site_display_name': site_display_name,
            'export_status_detail': export_status_detail,
            'export_fields': export_fields}

        subject = render_to_string(
            template_name='directories/notices/export_ready_subject.html', context=parms)
        subject = subject.strip('\n').strip('\r')

        body = render_to_string(
            template_name='directories/notices/export_ready_body.html', context=parms)

        email = Email(
            recipient=user.email,
            subject=subject,
            body=body)
        email.send()
