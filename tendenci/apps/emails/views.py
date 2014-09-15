from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from tendenci.core.emails.forms import EmailForm, AmazonSESVerifyEmailForm
from tendenci.core.emails.models import Email
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.base.http import Http403
from tendenci.core.perms.utils import has_perm

@login_required
def add(request, form_class=EmailForm, template_name="emails/edit.html"):
    if request.method == "POST":
        form = form_class(request.POST)

        if form.is_valid():
            email = form.save(request.user)

            return HttpResponseRedirect(reverse('email.view', args=[email.id]))
    else:
        form = form_class(initial={'sender':request.user.email,
                                   'sender_display': request.user.get_full_name,
                                   'reply_to': request.user.email})


    return render_to_response(template_name, {'form':form, 'email':None},
        context_instance=RequestContext(request))


def view(request, id, template_name="emails/view.html"):
    email = get_object_or_404(Email, pk=id)

    if not email.allow_view_by(request.user): raise Http403

    return render_to_response(template_name, {'email':email},
        context_instance=RequestContext(request))

@login_required
def edit(request, id, form_class=EmailForm, template_name="emails/edit.html"):
    email = get_object_or_404(Email, pk=id)
    if not email.allow_edit_by(request.user): raise Http403

    next = request.REQUEST.get("next", "")
    if request.method == "POST":
        form = form_class(request.POST, instance=email)

        if form.is_valid():
            email = form.save(request.user)

            if not next or ' ' in next:
                next = reverse('email.view', args=[email.id])

            return HttpResponseRedirect(next)
    else:
        form = form_class(instance=email)


    return render_to_response(template_name, {'form':form, 'email':email, 'next':next},
        context_instance=RequestContext(request))

def search(request, template_name="emails/search.html"):
    if request.user.profile.is_superuser:
        emails = Email.objects.all()
    else:
        emails = Email.objects.filter(status=True, status_detail='active')
    emails = emails.order_by('-create_dt')

    return render_to_response(template_name, {'emails':emails},
        context_instance=RequestContext(request))

def delete(request, id, template_name="emails/delete.html"):
    email = get_object_or_404(Email, pk=id)

    if not has_perm(request.user,'emails.delete_email',email): raise Http403

    if request.method == "POST":
        email.delete()
        return HttpResponseRedirect(reverse('email.search'))

    return render_to_response(template_name, {'email':email},
        context_instance=RequestContext(request))

@login_required
def amazon_ses_index(request, template_name="emails/amazon_ses/index.html"):
    # admin only
    if not request.user.profile.is_superuser:raise Http403

    return render_to_response(template_name,
        context_instance=RequestContext(request))


@login_required
def amazon_ses_verify_email(request, form_class=AmazonSESVerifyEmailForm,
                            template_name="emails/amazon_ses/verify_email.html"):
    # admin only
    if not request.user.profile.is_superuser:raise Http403

    from tendenci.core.emails.amazon_ses import AmazonSES
    form = form_class(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            email_addr = form.cleaned_data['email_address']
            amazon_ses = AmazonSES()
            result = amazon_ses.verifyEmailAddress(email_addr)

            messages.add_message(request, messages.INFO,
                                 _('The email address "%(email)s" has been sent to amazon to verify. \
                                 Please check your inbox and follow the instruction in the \
                                 email to complete the verification.' % {'email':email_addr}))

    return render_to_response(template_name, {'form':form},
        context_instance=RequestContext(request))

@login_required
def amazon_ses_list_verified_emails(request, template_name="emails/amazon_ses/list_verified_emails.html"):
    # admin only
    if not request.user.profile.is_superuser:raise Http403

    from tendenci.core.emails.amazon_ses import AmazonSES
    amazon_ses = AmazonSES()
    verified_emails = amazon_ses.listVerifiedEmailAddresses()
    if verified_emails:
        verified_emails = verified_emails.members
        verified_emails.sort()

    return render_to_response(template_name, {'verified_emails':verified_emails},
        context_instance=RequestContext(request))

@login_required
def amazon_ses_send_quota(request, template_name="emails/amazon_ses/send_quota.html"):
    # admin only
    if not request.user.profile.is_superuser:raise Http403

    from tendenci.core.emails.amazon_ses import AmazonSES
    amazon_ses = AmazonSES()
    send_quota = amazon_ses.getSendQuota()

    return render_to_response(template_name, {'send_quota':send_quota},
        context_instance=RequestContext(request))
