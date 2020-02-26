
from builtins import str

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.base.utils import create_salesforce_contact
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.contacts.models import Contact, Address, Phone, Email, URL
from tendenci.apps.contacts.forms import ContactForm, SubmitContactForm
from tendenci.apps.contacts.utils import listed_in_email_block
from tendenci.apps.profiles.models import Profile
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.perms.utils import has_perm, has_view_perm, get_query_filters, get_notice_recipients
from tendenci.apps.event_logs.models import EventLog

try: from tendenci.apps.notifications import models as notification
except: notification = None


@login_required
def details(request, id=None, template_name="contacts/view.html"):
    if not id: return HttpResponseRedirect(reverse('contacts'))
    contact = get_object_or_404(Contact, pk=id)

    if has_view_perm(request.user,'contacts.view_contact',contact):
        return render_to_resp(request=request, template_name=template_name,
            context={'contact': contact})
    else:
        raise Http403

def search(request, template_name="contacts/search.html"):
    if request.user.is_anonymous:
        raise Http403
    if not has_perm(request.user,'contacts.view_contact'):
        raise Http403

    query = request.GET.get('q', None)
    if get_setting('site', 'global', 'searchindex') and query:
        contacts = Contact.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'contacts.view_contact')
        contacts = Contact.objects.filter(filters).distinct()
        if not request.user.is_anonymous:
            contacts = contacts.select_related()

    contacts = contacts.order_by('-create_dt')

    return render_to_resp(request=request, template_name=template_name,
        context={'contacts':contacts})


def search_redirect(request):
    return HttpResponseRedirect(reverse('contacts'))

@login_required
def print_view(request, id, template_name="contacts/print-view.html"):
    contact = get_object_or_404(Contact, pk=id)

    if has_view_perm(request.user,'contacts.view_contact',contact):
        return render_to_resp(request=request, template_name=template_name,
            context={'contact': contact})
    else:
        raise Http403

@login_required
def add(request, form_class=ContactForm, template_name="contacts/add.html"):
    if has_perm(request.user,'contacts.add_contact'):

        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():
                contact = form.save(commit=False)
                # set up the user information
                contact.creator = request.user
                contact.creator_username = request.user.username
                contact.owner = request.user
                contact.owner_username = request.user.username
                contact.allow_anonymous_view = False
                contact.save()

                ObjectPermission.objects.assign(contact.creator, contact)

                return HttpResponseRedirect(reverse('contact', args=[contact.pk]))
        else:
            form = form_class()
            print(form_class())

        return render_to_resp(request=request, template_name=template_name,
            context={'form':form})
    else:
        raise Http403

@login_required
def delete(request, id, template_name="contacts/delete.html"):
    contact = get_object_or_404(Contact, pk=id)

    if has_perm(request.user,'contacts.delete_contact'):
        if request.method == "POST":
            contact.delete()
            return HttpResponseRedirect(reverse('contact.search'))

        return render_to_resp(request=request, template_name=template_name,
            context={'contact': contact})
    else:
        raise Http403


def index(request, form_class=SubmitContactForm, template_name="form.html"):

    if request.method == "GET":
        # event-log view
        EventLog.objects.log(instance=Contact(), action='viewed')

    if request.method == "POST":
        event_log_dict = {}
        form = form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')

            if listed_in_email_block(email):
                # listed in the email blocks - it's a spam email we want to block
                # log the spam
                EventLog.objects.log()

                # redirect normally so they don't suspect
                return HttpResponseRedirect(reverse('form.confirmation'))

            address = form.cleaned_data.get('address')
            city = form.cleaned_data.get('city')
            state = form.cleaned_data.get('state')
            zipcode = form.cleaned_data.get('zipcode')
            country = form.cleaned_data.get('country')
            phone = form.cleaned_data.get('phone')
            url = form.cleaned_data.get('url')
            message = form.cleaned_data.get('message')

            exists = User.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact=last_name,
                email__iexact=email,
            ).exists()

            if request.user.is_anonymous:
                username = first_name.replace(' ', '')
                if last_name:
                    username = username + '_' + last_name.replace(' ', '')
                username = username.lower()
                try:
                    User.objects.get(username=username)
                    x = User.objects.filter(first_name=first_name).count()
                    username = username + '_' + str(x)
                except User.DoesNotExist:
                    pass

                contact_user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )

                contact_user.is_active = False
                contact_user.save()
                profile = Profile(user=contact_user, owner=contact_user, creator=User.objects.get(pk=1),
                                  address=address, country=country, city=city, state=state,
                                  url=url, phone=phone, zipcode=zipcode)
                profile.save()
                create_salesforce_contact(profile)  # Returns sf_id

                # if exists:
                #     event_log_dict['description'] = 'logged-out submission as existing user'
                # else:
                event_log_dict['description'] = 'logged-out submission as new user'

            else:  # logged in user
                self_submit = all([
                    request.user.first_name.lower().strip() == first_name.lower().strip(),
                    request.user.last_name.lower().strip() == last_name.lower().strip(),
                    request.user.email.lower().strip() == email.lower().strip(),
                ])

                contact_user = request.user

                if exists:
                    if self_submit:
                        event_log_dict['description'] = 'logged-in submission as self'
                    else:
                        event_log_dict['description'] = 'logged-in submission as existing user'
                else:
                    event_log_dict['description'] = 'logged-in submission as non-existing user'

            contact_kwargs = {
                'first_name': first_name,
                'last_name': last_name,
                'message': message,
                'user': contact_user,
            }

            contact = Contact(**contact_kwargs)
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
                obj_address.save()  # saves object
                contact.addresses.add(obj_address)  # saves relationship

            if phone:
                obj_phone = Phone(number=phone)
                obj_phone.save()  # saves object
                contact.phones.add(obj_phone)  # saves relationship

            if email:
                obj_email = Email(email=email)
                obj_email.save()  # saves object
                contact.emails.add(obj_email)  # saves relationship

            if url:
                obj_url = URL(url=url)
                obj_url.save()  # saves object
                contact.urls.add(obj_url)  # saves relationship

            site_name = get_setting('site', 'global', 'sitedisplayname')
            message_link = get_setting('site', 'global', 'siteurl')

            # send notification to administrators
            # get admin notice recipients
            recipients = get_notice_recipients('module', 'contacts', 'contactrecipients')
            if recipients:
                if notification:
                    extra_context = {
                    'reply_to': email,
                    'contact': contact,
                    'first_name': first_name,
                    'last_name': last_name,
                    'address': address,
                    'city': city,
                    'state': state,
                    'zipcode': zipcode,
                    'country': country,
                    'phone': phone,
                    'email': email,
                    'url': url,
                    'message': message,
                    'message_link': message_link,
                    'site_name': site_name,
                    }
                    notification.send_emails(recipients, 'contact_submitted', extra_context)

            # event-log (logged in)
            event_log = EventLog.objects.log(
                instance=contact,
                user=contact_user,
                action='submitted',
                **event_log_dict
            )

            event_log.url = contact.get_absolute_url()
            event_log.save()

            return HttpResponseRedirect(reverse('form.confirmation'))
        else:
            return render_to_resp(request=request, template_name=template_name,
                context={'form': form})

    form = form_class()
    return render_to_resp(request=request, template_name=template_name,
        context={'form': form})


def confirmation(request, form_class=SubmitContactForm, template_name="form-confirmation.html"):
    return render_to_resp(request=request, template_name=template_name)
