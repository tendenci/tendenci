from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.template import RequestContext
from django.db.models import Q

from explorer import app_settings
from explorer.views import change_permission
from tendenci.apps.explorer_extensions.models import DatabaseDumpFile
from tendenci.apps.explorer_extensions.forms import DatabaseDumpForm


def get_app_permissions(request):
    return {'can_view': app_settings.EXPLORER_PERMISSION_VIEW(request.user),
            'can_change': app_settings.EXPLORER_PERMISSION_CHANGE(request.user)}

@change_permission
def export_page(request):
    ctx = {}
    ctx.update(get_app_permissions(request))

    form = None
    if request.method == 'POST':
        form = DatabaseDumpForm(request.POST)
        if form.is_valid():
            print "Form submitted is valid!"
            if can_create_dump():
                # TODO: run management command
                pass
            else:
                # TODO: throw an error
                pass
    else:
        form = DatabaseDumpForm()


    # get all active DB Dump Files
    # if current existing DB Dump Files are less than the limit, enable form submission
    db_objs = DatabaseDumpFile.objects.filter(~Q(status='expired'))

    ctx['objects'] = db_objs
    if can_create_dump():
        ctx['enable_form'] = True

    ctx['form'] = form
    return render_to_response("explorer/export_page.html", ctx,
                                context_instance=RequestContext(request))

def can_create_dump():
    db_objs = DatabaseDumpFile.objects.filter(~Q(status='expired'))
    return db_objs.count() < 3
