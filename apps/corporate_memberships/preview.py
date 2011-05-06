from django.contrib.formtools.preview import FormPreview
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

#from corporate_memberships.models import CorporateMembership

class CorpMembRenewFormPreview(FormPreview):
    preview_template = 'corporate_memberships/renew_preview.html'
    form_template = 'corporate_memberships/renew.html'

    def done(self, request, cleaned_data):
        # Do something with the cleaned_data, then redirect
        # to a "success" page.
        return HttpResponseRedirect(reverse('corp_memb.renew_conf'))
