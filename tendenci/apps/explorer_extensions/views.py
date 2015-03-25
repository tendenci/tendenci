from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.template import RequestContext

from explorer import app_settings
from explorer.views import change_permission


def get_app_permissions(request):
    return {'can_view': app_settings.EXPLORER_PERMISSION_VIEW(request.user),
            'can_change': app_settings.EXPLORER_PERMISSION_CHANGE(request.user)}

@change_permission
def export_page(request):
    ctx = {}
    ctx.update(get_app_permissions(request))
    return render_to_response("explorer/export_page.html", ctx,
                                context_instance=RequestContext(request))
