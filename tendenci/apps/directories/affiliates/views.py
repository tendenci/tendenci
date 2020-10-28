from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, Http404
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.base.http import Http403
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.directories.models import Directory
from tendenci.apps.site_settings.utils import get_setting

from .forms import RequestAssociateForm
from .utils import get_allowed_affiliate_types
from .models import AffiliateRequest

@login_required
def request_associate(request, to_directory_id, form_class=RequestAssociateForm,
                         template_name="directories/affiliates/request_associate.html"):
    if not get_setting('module', 'directories', 'affiliates_enabled'):
        raise Http404
    
    to_directory = get_object_or_404(Directory, pk=to_directory_id)
    if not to_directory.allow_associate_by(request.user):
        raise Http404
    
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
            'to_directory': to_directory,
            'corp_type': corp_type,
            'allowed_member_types': allowed_member_types,
            'request_form': request_form,})