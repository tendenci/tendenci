from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from donations.forms import DonationForm
from donations.utils import donation_inv_add, donation_email_user
from donations.models import Donation
from site_settings.utils import get_setting
from base.http import Http403
from base.utils import tcurrency
from event_logs.models import EventLog
from perms.utils import get_notice_recipients, is_admin
from perms.utils import has_perm
from base.utils import get_unique_username
from profiles.models import Profile

try:
    from notification import models as notification
except:
    notification = None


def add(request, form_class=DonationForm, template_name="donations/add.html"):
    if request.method == "POST":
        form = form_class(request.POST, user=request.user)
        
        if form.is_valid():
            donation = form.save(commit=False)
            donation.payment_method = donation.payment_method.lower()
            # we might need to create a user record if not exist
            if request.user.is_authenticated():
                user = request.user
            else:
                try:
                    user = User.objects.get(email=donation.email)
                except:
                    user = request.user

            if not user.is_anonymous():
                donation.user = user
                donation.creator = user
                donation.creator_username = user.username
            else:
                # this is anonymous user donating and we didn't find their user record in the system,
                # so add a new user
                user = User()
                user.first_name = donation.first_name
                user.last_name = donation.last_name
                user.email = donation.email
                user.username = get_unique_username(user)
                user.set_password(User.objects.make_random_password(length=8))
                user.is_active = 0
                user.save()
                
                profile_kwarg = {'user':user,
                                 'company':donation.company,
                                 'address':donation.address,
                                 'address2':donation.address2,
                                 'city':donation.city,
                                 'state':donation.state,
                                 'zipcode':donation.zip_code,
                                 'country':donation.country,
                                 'email':donation.email,
                                 'phone':donation.phone}
                if request.user.is_anonymous():
                    profile_kwarg['creator'] = user
                    profile_kwarg['creator_username'] = user.username
                    profile_kwarg['owner'] = user
                    profile_kwarg['owner_username'] = user.username
                else:
                    profile_kwarg['creator'] = request.user
                    profile_kwarg['creator_username'] = request.user.username
                    profile_kwarg['owner'] = request.user
                    profile_kwarg['owner_username'] = request.user.username
                    
                profile = Profile.objects.create(**profile_kwarg)
                profile.save()
                
            donation.save(user)
            
            # create invoice
            invoice = donation_inv_add(user, donation)
            # updated the invoice_id for mp, so save again
            donation.save(user)
            
            if is_admin(request.user): 
                if donation.payment_method in ['paid - check', 'paid - cc']:
                    # the admin accepted payment - mark the invoice paid
                    invoice.tender(request.user)
                    invoice.make_payment(request.user, donation.donation_amount)
            
            # log an event for invoice add
            log_defaults = {
                'event_id' : 311000,
                'event_data': '%s (%d) added by %s' % (invoice._meta.object_name, invoice.pk, request.user),
                'description': '%s added' % invoice._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': invoice,
            }
            EventLog.objects.log(**log_defaults)  
            
            # log an event for donation add
            log_defaults = {
                'event_id' : 511000,
                'event_data': '%s (%d) added by %s' % (donation._meta.object_name, donation.pk, request.user),
                'description': '%s added' % donation._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': donation,
            }
            EventLog.objects.log(**log_defaults)
            
            # send notification to administrators
            # get admin notice recipients
            if not donation.payment_method.lower() in ['cc', 'credit card']:
                # email to admin (if payment type is credit card email is not sent until payment confirmed)
                recipients = get_notice_recipients('module', 'donations', 'donationsrecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'donation': donation,
                            'invoice': invoice,
                            'request': request,
                        }
                        notification.send_emails(recipients,'donation_added', extra_context)
            
            # email to user 
            email_receipt = form.cleaned_data['email_receipt']
            if email_receipt:
                donation_email_user(request, donation, invoice)
            
            # redirect to online payment or confirmation page
            if donation.payment_method.lower() in ['cc', 'credit card']:
                return HttpResponseRedirect(reverse('payments.views.pay_online', args=[invoice.id, invoice.guid]))
            else:
                return HttpResponseRedirect(reverse('donation.add_confirm', args=[donation.id]))
    else:
        form = form_class(user=request.user)

    currency_symbol = get_setting("site", "global", "currencysymbol")
    if not currency_symbol: currency_symbol = "$"
       
    return render_to_response(template_name, {'form':form, 'currency_symbol': currency_symbol}, 
        context_instance=RequestContext(request))
    
def add_confirm(request, id, template_name="donations/add_confirm.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))

@login_required
def view(request, id=None, template_name="donations/view.html"):
    donation = get_object_or_404(Donation, pk=id)
    if not has_perm(request.user,'donations.view_donation'): raise Http403
    
    donation.donation_amount = tcurrency(donation.donation_amount)
    return render_to_response(template_name, {'donation':donation}, 
        context_instance=RequestContext(request))
    
def receipt(request, id, guid, template_name="donations/receipt.html"):
    donation = get_object_or_404(Donation, pk=id, guid=guid)
    
    donation.donation_amount = tcurrency(donation.donation_amount)
    
    if (not donation.invoice) or donation.invoice.balance > 0 or (not donation.invoice.is_tendered):
        template_name="donations/view.html"
    return render_to_response(template_name, {'donation':donation}, 
        context_instance=RequestContext(request))
  
@login_required  
def search(request, template_name="donations/search.html"):
    query = request.GET.get('q', None)
    if get_setting('site', 'global', 'searchindex') and query:
        donations = Donation.objects.search(query)
    else:
        donations = Donation.objects.all()

    log_defaults = {
        'event_id' : 514000,
        'event_data': '%s searched by %s' % ('Donation', request.user),
        'description': '%s searched' % 'Donation',
        'user': request.user,
        'request': request,
        'source': 'donations'
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {'donations':donations}, 
        context_instance=RequestContext(request))
    
    
    