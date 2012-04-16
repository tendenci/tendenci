from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser

from event_logs.models import EventLog

from site_settings.utils import get_setting
from contacts.models import Contact, Address, Phone, Email, URL
from form_builder.forms import ContactForm
from form_builder.utils import listed_in_email_block


from perms.utils import get_notice_recipients
try: from notification import models as notification
except: notification = None

def index(request, form_class=ContactForm, template_name="form.html"):

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email', None)
            first_name = form.cleaned_data.get('first_name', None)
            last_name = form.cleaned_data.get('last_name', None)
            
            if listed_in_email_block(email):
                # listed in the email blocks - it's a spam email we want to block
                # log the spam
                log_defaults = {
                    'event_id' : 130999,
                    'event_data': 'SPAM detected in email from  %s %s, %s.' \
                                    % (first_name, last_name, email),
                    'description': 'email spam detected',
                    'user': request.user,
                    'request': request,
                }
                EventLog.objects.log(**log_defaults)
                
                # redirect normally so they don't suspect
                return HttpResponseRedirect(reverse('form.confirmation'))
            
            address = form.cleaned_data.get('address', None)
            city = form.cleaned_data.get('city', None)
            state = form.cleaned_data.get('state', None)
            zipcode = form.cleaned_data.get('zipcode', None)
            country = form.cleaned_data.get('country', None)
            phone = form.cleaned_data.get('phone', None)
            
            url = form.cleaned_data.get('url', None)
            message = form.cleaned_data.get('message', None)

            contact_kwargs = {
                'first_name': first_name,
                'last_name': last_name,
                'message': message,
            } 
            contact = Contact(**contact_kwargs)
            contact.creator_id = 1 # TODO: decide if we should use tendenci base model
            contact.owner_id = 1 # TODO: decide if we should use tendenci base model
            contact.allow_anonymous_view = False
            contact.save()

            if address or city or state or zipcode or country:
                address_kwargs = {
                    'address': address,
                    'city': city,
                    'state': state,
                    'zipcode': zipcode,
                    'country': country,
                }
                obj_address = Address(**address_kwargs)
                obj_address.save() # saves object
                contact.addresses.add(obj_address) # saves relationship

            if phone:
                obj_phone = Phone(number=phone)
                obj_phone.save() # saves object
                contact.phones.add(obj_phone) # saves relationship

            if email:
                obj_email = Email(email=email)
                obj_email.save() # saves object
                contact.emails.add(obj_email) # saves relationship

            if url:
                obj_url = URL(url=url)
                obj_url.save() # saves object
                contact.urls.add(obj_url) # saves relationship

            site_name = get_setting('site', 'global', 'sitedisplayname')
            message_link = get_setting('site', 'global', 'siteurl')

            # send notification to administrators
            # get admin notice recipients
            recipients = get_notice_recipients('module', 'contacts', 'contactrecipients')
            if recipients:
                if notification:
                    extra_context = {
                    'reply_to': email,
                    'contact':contact,
                    'first_name':first_name,
                    'last_name':last_name,
                    'address':address,
                    'city':city,
                    'state':state,
                    'zipcode':zipcode,
                    'country':country,
                    'phone':phone,
                    'email':email,
                    'url':url,
                    'message':message,
                    'message_link':message_link,
                    'site_name':site_name,
                    }
                    notification.send_emails(recipients,'contact_submitted', extra_context)

            try: user = User.objects.filter(email=email)[0]
            except: user = None

            if user:
                event_user = user
                event_id = 125115
            else:
                event_user = AnonymousUser()
                event_id = 125114

            log_defaults = {
                'event_id' : event_id,
                'event_data': 'Contact Form (id:%d) submitted by %s' % (contact.pk, email),
                'description': '%s added' % contact._meta.object_name,
                'user': event_user,
                'request': request,
                'instance': contact,
            }
            EventLog.objects.log(**log_defaults)

            return HttpResponseRedirect(reverse('form.confirmation'))
        else:
            return render_to_response(template_name, {'form': form}, 
                context_instance=RequestContext(request))

    form = form_class()
    return render_to_response(template_name, {'form': form}, 
        context_instance=RequestContext(request))

def confirmation(request, form_class=ContactForm, template_name="form-confirmation.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))











