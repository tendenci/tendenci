import os.path
import subprocess
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.conf import settings
from tendenci.apps.wp_importer.forms import BlogImportForm
from tendenci.apps.wp_importer.tasks import WPImportTask
from tendenci.apps.base.http import MissingApp
from django.contrib import messages
from django.utils.translation import ugettext as _
from djcelery.models import TaskMeta


@login_required
def index(request, template_name="wp_importer/index.html"):
    if "tendenci.apps.articles" not in settings.INSTALLED_APPS:
        raise MissingApp(_('Oops, you must install Articles so that we can import your posts from WordPress!'))
    if request.method == 'POST':
        form = BlogImportForm(request.POST, request.FILES)
        try:
            if form.is_valid() and request.FILES['blog'].name.endswith('xml') and request.FILES['blog'].size < 20*1024*1024 and request.user:
                upload = form.save(commit=False)
                upload.author = request.user
                upload = form.save()
                file_name = os.path.join(settings.MEDIA_ROOT, 'blogimport', request.FILES['blog'].name)

                result = WPImportTask.delay(file_name, request.user)
                #uncomment the next line if there is no celery server yet.
                #result.wait()
                subprocess.Popen(['python', 'manage.py', 'celeryd_detach'])

                return redirect("detail", result.task_id)

            elif not request.FILES['blog'].name.endswith('xml'):
                messages.add_message(
                    request,
                    messages.INFO,
                    _('Oops, only upload XML files!')
                )

            elif not request.FILES['blog'].size < 20*1024*1024:
                messages.add_message(
                    request,
                    messages.INFO,
                    _('Oops, only upload files smaller than 20 MB!')
                )

        except ValueError:
            messages.add_message(request, messages.INFO, _('Oops, please login before uploading a blog!'))
            return redirect('auth_login')

    else:
        form = BlogImportForm()

    return render_to_response(template_name, {'form':form},
        context_instance=RequestContext(request))

@login_required
def detail(request, task_id, template_name="wp_importer/detail.html"):
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        #tasks database entries are not created at once.
        #instead of raising 404 we'll assume that there will be one for
        #the id.
        task = None

    if task and task.status == "SUCCESS":
        messages.add_message(
            request,
            messages.INFO,
            _('Your blog has been imported!')
        )
        return render_to_response(template_name, {},
            context_instance=RequestContext(request))

    messages.add_message(
        request,
        messages.INFO,
        _("Your site import is being processed. You will receive an email at %s when the import is complete." % request.user.email)
    )

    return render_to_response(template_name, {},
        context_instance=RequestContext(request))
