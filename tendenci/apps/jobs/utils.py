# settings - jobspaymenttypes, jobsrequirespayment
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.jobs.models import Job, JobPricing
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.payments.models import Payment
from tendenci.apps.site_settings.utils import get_setting


def get_payment_method_choices(user):
    if user.profile.is_superuser:
        return (('paid - check', _('User paid by check')),
                ('paid - cc', _('User paid by credit card')),
                ('Credit Card', _('Make online payment NOW')),)
    else:
        job_payment_types = get_setting('module', 'jobs', 'jobspaymenttypes')
        if job_payment_types:
            job_payment_types_list = job_payment_types.split(',')
            job_payment_types_list = [item.strip() for item in job_payment_types_list]

            return [(item, item) for item in job_payment_types_list]
        else:
            return ()


def get_job_unique_slug(slug):
    # check if this slug already exists
    jobs = Job.objects.filter(slug__istartswith=slug)

    if jobs:
        t_list = [j.slug[len(j.slug):] for j in jobs]
        num = 1
        while str(num) in t_list:
            num += 1
        slug = '%s-%s' % (slug, str(num))

    return slug


def job_set_inv_payment(user, job, pricing):
    if get_setting('module', 'jobs', 'jobsrequirespayment'):
        if not job.invoice:
            inv = Invoice()
            inv.object_type = ContentType.objects.get(app_label=job._meta.app_label,
                                              model=job._meta.model_name)
            inv.object_id = job.id
            inv.title = _("Job Add Invoice")
            inv.bill_to = job.contact_name
            first_name = ''
            last_name = ''
            if job.contact_name:
                name_list = job.contact_name.split(' ')
                if len(name_list) >= 2:
                    first_name = name_list[0]
                    last_name = ' '.join(name_list[1:])
            inv.bill_to_first_name = first_name
            inv.bill_to_last_name = last_name
            inv.bill_to_company = job.contact_company
            inv.bill_to_address = job.contact_address
            inv.bill_to_city = job.contact_city
            inv.bill_to_state = job.contact_state
            inv.bill_to_zip_code = job.contact_zip_code
            inv.bill_to_country = job.contact_country
            inv.bill_to_phone = job.contact_phone
            inv.bill_to_fax = job.contact_fax
            inv.bill_to_email = job.contact_email
            inv.ship_to = job.contact_name
            inv.ship_to_first_name = first_name
            inv.ship_to_last_name = last_name
            inv.ship_to_company = job.contact_company
            inv.ship_to_address = job.contact_address
            inv.ship_to_city = job.contact_city
            inv.ship_to_state = job.contact_state
            inv.ship_to_zip_code = job.contact_zip_code
            inv.ship_to_country = job.contact_country
            inv.ship_to_phone = job.contact_phone
            inv.ship_to_fax = job.contact_fax
            inv.ship_to_email =job.contact_email
            inv.terms = _("Due on Receipt")
            inv.due_date = datetime.now()
            inv.ship_date = datetime.now()
            inv.message = _('Thank You.')
            inv.status = True

            inv.total = get_job_price(user, job, pricing)
            inv.subtotal = inv.total
            inv.balance = inv.total
            inv.estimate = True
            inv.status_detail = 'estimate'

            tax = 0
            if pricing.include_tax:
                tax = inv.total * pricing.tax_rate
                total = tax + inv.total
                inv.tax = tax
                inv.total = total
                inv.subtotal = total
                inv.balance = total

            if user and not user.is_anonymous():
                inv.set_creator(user)
                inv.set_owner(user)

            inv.save(user)

            # tender the invoice
            inv.tender(user)

            # update job
            job.invoice = inv
            job.save()

            if user.profile.is_superuser:
                if job.payment_method in ['paid - cc', 'paid - check', 'paid - wire transfer']:
                    boo_inv = inv.tender(user)

                    # payment
                    payment = Payment()
                    boo = payment.payments_pop_by_invoice_user(user, inv, inv.guid)
                    payment.mark_as_paid()
                    payment.method = job.payment_method
                    payment.save(user)

                    # this will make accounting entry
                    inv.make_payment(user, payment.amount)


def get_job_price(user, job, pricing):
    return pricing.get_price_for_user(
                      user=user,
                      list_type=job.list_type)


def is_free_listing(user, pricing_id, list_type):
    """
    Check if a directory listing with the specified pricing and list type is free.
    """
    try:
        pricing_id = int(pricing_id)
    except:
        pricing_id = 0
    [pricing] = pricing_id and JobPricing.objects.filter(pk=pricing_id)[:1] or [None]

    if pricing:
        return pricing.get_price_for_user(user, list_type=list_type) <= 0
    return False


def pricing_choices(user):
    """
    Since the list type of a job cannot be determined without the job,
    Both regular and premium price will be included in the label.
    """
    choices = []
    pricings = JobPricing.objects.all()
    member = False
    if user.profile:
        if user.profile.is_member:
            member = True

    for pricing in pricings:
        if member:
            prices = "%s/%s" % (pricing.regular_price_member, pricing.premium_price_member)
        else:
            prices = "%s/%s" % (pricing.regular_price, pricing.premium_price)

        label = "%s: %s Days for %s" % (pricing.get_title(), pricing.duration, prices)
        choices.append((pricing.pk, label))
    return choices
