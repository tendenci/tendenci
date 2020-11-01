from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponseRedirect, get_object_or_404, redirect, Http404
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from tendenci.apps.base.http import Http403
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.directories.models import Directory, Affiliateship
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.notifications import models as notification

from .forms import RequestAssociateForm
from .utils import get_allowed_affiliate_types
from .models import AffiliateRequest

@login_required
def request_associate(request, to_directory_id, form_class=RequestAssociateForm,
                         template_name="directories/affiliates/request_associate.html"):
    if not get_setting('module', 'directories', 'affiliates_enabled'):
        raise Http404
    
    to_directory = get_object_or_404(Directory, pk=to_directory_id)

    # Check user permission
    if not to_directory.allow_associate_by(request.user):
        raise Http404
    
    # Get a list of allowed member types
    if get_setting('module', 'directories', 'affiliation_limited'):
        corp_type = to_directory.get_corp_type()
        allowed_member_types = get_allowed_affiliate_types(corp_type)
        
        if not allowed_member_types:
            raise Http404

        corp_type = corp_type.name
        allowed_member_types = ', '.join([aat.name for aat in allowed_member_types])
    else:
        corp_type = None
        allowed_member_types = None
    
    request_form = form_class(request.POST or None, request=request,
                              to_directory=to_directory,)

    if request.method == "POST":
        if request_form.is_valid():
            request_email = request_form.save()

            msg_string = _('Successfully submitted the affiliate request to the owner of %s') \
                    % str(request_email.affiliate_request.to_directory)
            messages.add_message(request, messages.SUCCESS, msg_string)
            
            return redirect("directory.search")

    return render_to_resp(request=request, template_name=template_name,
        context={
            'directory': to_directory,
            'corp_type': corp_type,
            'allowed_member_types': allowed_member_types,
            'request_form': request_form,})


@csrf_protect
@login_required
def approve(request, affiliate_request_id):
    """
    Approve an affiliate request.
    """
    if not get_setting('module', 'directories', 'affiliates_enabled'):
        raise Http404

    # Get the affiliate_request and directory
    affiliate_request = get_object_or_404(AffiliateRequest, id=affiliate_request_id)
    directory = affiliate_request.to_directory

    # Check user permission
    if not directory.allow_approve_affiliations_by(request.user):
        raise Http403

    if request.method in ["POST"]:
        from_directory = affiliate_request.from_directory
        if not Affiliateship.objects.filter(directory=directory, affiliate=from_directory).exists():
            # Add affiliate to the directory
            Affiliateship.objects.create(
                directory=directory,
                affiliate=from_directory,
                creator=request.user)
    
            # Email to the submitter of the affiliate request
            site_display_name = get_setting('site', 'global', 'sitedisplayname')
            site_url = get_setting('site', 'global', 'siteurl')
            params = {
                'SITE_GLOBAL_SITEDISPLAYNAME': site_display_name,
                'SITE_GLOBAL_SITEURL': site_url,
                'directory': directory,
                'from_directory': from_directory,
                'first_name': affiliate_request.creator.first_name,
                'reply_to': request.user.email,
            }
            notification.send_emails([affiliate_request.creator.email],
                    'affiliate_approved_to_submitter', params)
        
    
            msg_string = _('Successfully approved the affiliate request from %s') \
                    % str(from_directory)
            messages.add_message(request, messages.SUCCESS, msg_string)
        
        # Remove the request
        affiliate_request.delete()
        
        if 'ajax' in request.POST:
            return HttpResponse('Ok')

    return HttpResponseRedirect(reverse('directory', args=[directory.slug]))


@csrf_protect
@login_required
def reject(request, affiliate_request_id):
    """
    Reject an affiliate request.
    """
    if not get_setting('module', 'directories', 'affiliates_enabled'):
        raise Http404

    # Get the affiliate_request and directory
    affiliate_request = get_object_or_404(AffiliateRequest, id=affiliate_request_id)
    directory = affiliate_request.to_directory

    # Check user permission
    if not directory.allow_reject_affiliations_by(request.user):
        raise Http403

    if request.method in ["POST"]:
        from_directory = affiliate_request.from_directory
        if not Affiliateship.objects.filter(directory=directory, affiliate=from_directory).exists():
    
            # Email to the submitter of the affiliate request rejected
            site_display_name = get_setting('site', 'global', 'sitedisplayname')
            site_url = get_setting('site', 'global', 'siteurl')
            params = {
                'SITE_GLOBAL_SITEDISPLAYNAME': site_display_name,
                'SITE_GLOBAL_SITEURL': site_url,
                'directory': directory,
                'from_directory': from_directory,
                'first_name': affiliate_request.creator.first_name,
                'reply_to': request.user.email,
            }

            notification.send_emails([affiliate_request.creator.email],
                    'affiliate_rejected_to_submitter', params)
        
    
            msg_string = _('Successfully rejected the affiliate request from %s') \
                    % str(from_directory)
        else:
            msg_string = _('%s us already associated.') \
                    % str(from_directory)
        messages.add_message(request, messages.SUCCESS, msg_string)
        
        # Remove the request
        affiliate_request.delete()
        
        if 'ajax' in request.POST:
            return HttpResponse('Ok')

    return HttpResponseRedirect(reverse('directory', args=[directory.slug]))


@login_required
def cancel(request, affiliate_request_id):
    """
    Cancel an affiliate request (by owner or superuser).
    """
    if not get_setting('module', 'directories', 'affiliates_enabled'):
        raise Http404

    # Get the affiliate_request and directory
    affiliate_request = get_object_or_404(AffiliateRequest, id=affiliate_request_id)
    from_directory = affiliate_request.from_directory

    # Check user permission
    if not any([request.user.is_superuser,
                from_directory.is_owner(request.user)]):
        raise Http403
    
    msg_string = _('Successfully canceled the affiliate request with %s') \
                % str(affiliate_request.to_directory)
    messages.add_message(request, messages.SUCCESS, msg_string)

    # delete the request
    affiliate_request.delete()

    return HttpResponseRedirect(reverse('directory', args=[from_directory.slug]))


@login_required
def delete_affiliate(request, directory_id, from_directory_id):
    """
    Delete an affiliate. 
    """
    if not get_setting('module', 'directories', 'affiliates_enabled'):
        raise Http404

    # Get the affiliate_request and directory
    directory = get_object_or_404(Directory, id=directory_id)
    from_directory = get_object_or_404(Directory, id=from_directory_id)
    
    # Check user permission
    if not any([request.user.is_superuser,
                directory.is_owner(request.user)]):
        raise Http403
    
    msg_string = _('Successfully removed the affiliate %s') \
                % str(from_directory)
    messages.add_message(request, messages.SUCCESS, msg_string)

    # delete the request
    directory.affiliates.remove(from_directory)

    return HttpResponseRedirect(reverse('directory', args=[directory.slug]))


@login_required
def requests_list(request, directory_id, template_name="directories/affiliates/requests_list.html"):
    if not get_setting('module', 'directories', 'affiliates_enabled'):
        raise Http404
    
    directory = get_object_or_404(Directory, pk=directory_id)

    # Check user permission
    if not any([request.user.is_superuser,
                directory.is_owner(request.user)]):
        raise Http403
    
    affiliate_requests = AffiliateRequest.objects.filter(to_directory=directory)
    
    return render_to_resp(request=request, template_name=template_name,
        context={
            'directory': directory,
            'affiliate_requests': affiliate_requests,
            'count': affiliate_requests.count()})





