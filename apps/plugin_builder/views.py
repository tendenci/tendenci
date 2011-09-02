from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.management import call_command

from base.http import Http403
from perms.utils import update_perms_and_save, has_perm, is_admin
from plugin_builder.models import Plugin

@login_required
def write_plugin(request, id):
    if not is_admin(request.user):
        raise Http403
    
    plugin = get_object_or_404(Plugin, id=id)
    
    call_command('t5plugin', plugin.single_caps, plugin.single_lower, plugin.plural_caps, plugin.plural_lower)
    
