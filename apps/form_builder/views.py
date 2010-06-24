from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from contacts.models import Contact, Address, Phone, Email, URL
from form_builder.forms import ContactForm

def index(request, form_class=ContactForm, template_name="form.html"):

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():

            first_name = form.cleaned_data.get('first_name', None)
            last_name = form.cleaned_data.get('last_name', None)
            address = form.cleaned_data.get('address', None)
            city = form.cleaned_data.get('city', None)
            state = form.cleaned_data.get('state', None)
            zipcode = form.cleaned_data.get('zipcode', None)
            country = form.cleaned_data.get('country', None)
            phone = form.cleaned_data.get('phone', None)
            email = form.cleaned_data.get('email', None)
            url = form.cleaned_data.get('url', None)
            message = form.cleaned_data.get('message', None)

            contact_kwargs = {
                'first_name': first_name,
                'last_name': last_name,
                'message': message,
            } 
            contact = Contact(**contact_kwargs)
            contact.creator = request.user
            contact.owner = request.user
            contact.save()

            if address or city or state or zipcode or country:
                address_kwargs = {
                    'city': city,
                    'state': state,
                    'zipcode': zipcode,
                    'country': country,
                }
                obj_address = Address(**address_kwargs)
                obj_address.save()
                contact.addresses.add(obj_address)

            if phone:
                obj_phone = Phone(number=phone)
                obj_phone.save()
                contact.phones.add(obj_phone)

            if email:
                obj_email = Email(email=email)
                obj_email.save()
                contact.emails.add(obj_email)

            if url:
                obj_url = URL(url=url)
                obj_url.save()
                contact.urls.add(obj_url)

            # TODO: log submission event
            return HttpResponseRedirect(reverse('form.confirmation'))
        else:
            return render_to_response(template_name, {'form': form}, 
                context_instance=RequestContext(request))

    form = form_class(initial={'first_name':'Eloy', 'email':'ezuniga@schipul.com', 'message':'I want Tendenci'})
    return render_to_response(template_name, {'form': form}, 
        context_instance=RequestContext(request))

def confirmation(request, form_class=ContactForm, template_name="form-confirmation.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))











