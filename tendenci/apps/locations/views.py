from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.base.http import Http403
from tendenci.apps.base.decorators import password_required
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import (has_perm, has_view_perm,
    update_perms_and_save, get_query_filters)
from tendenci.apps.perms.decorators import admin_required
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.exports.utils import run_export_task
from tendenci.apps.files.models import File
# from djcelery.models import TaskMeta

from tendenci.apps.locations.models import Location, LocationImport
from tendenci.apps.locations.forms import LocationForm, LocationFilterForm
from tendenci.apps.locations.utils import get_coordinates
from tendenci.apps.locations.importer.forms import UploadForm, ImportMapForm
from tendenci.apps.locations.importer.utils import is_import_valid, parse_locs_from_csv
from tendenci.apps.locations.importer.tasks import ImportLocationsTask
from tendenci.apps.imports.utils import render_excel


@is_enabled('locations')
def detail(request, slug, template_name="locations/view.html"):
    location = get_object_or_404(Location, slug=slug)

    if has_view_perm(request.user,'locations.view_location',location):
        EventLog.objects.log(instance=location)
        return render_to_resp(request=request, template_name=template_name,
            context={'location': location})
    else:
        raise Http403


@is_enabled('locations')
def search(request, template_name="locations/search.html"):
    filters = get_query_filters(request.user, 'locations.view_location')
    locations = Location.objects.filter(filters).distinct()

    if not request.user.is_anonymous:
        locations = locations.select_related()

    data = {'country':request.POST.get('country', ''),
            'state':request.POST.get('state', ''),
            'city':request.POST.get('city', '')}
    form = LocationFilterForm(data, request.POST or None)

    if request.method == 'POST' and form.is_valid():
        locations = form.filter_results(locations)

    locations = locations.order_by('location_name')

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'locations':locations, 'form':form})


def search_redirect(request):
    return HttpResponseRedirect(reverse('locations'))


@is_enabled('locations')
def nearest(request, template_name="locations/nearest.html"):
    locations = []
    lat, lng = None, None
    query = request.GET.get('q')
    filters = get_query_filters(request.user, 'locations.view_location')

    if query:
        lat, lng = get_coordinates(address=query)

    all_locations = Location.objects.filter(filters).distinct()
    if not request.user.is_anonymous:
        all_locations = all_locations.select_related()

    if all((lat,lng)):
        for location in all_locations:
            location.distance = location.get_distance2(lat, lng)
            if location.distance is not None:
                locations.append(location)
            locations.sort(key=lambda x: x.distance)

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={
        'locations':locations,
        'origin': {'lat':lat,'lng':lng},
        })


@is_enabled('locations')
def print_view(request, id, template_name="locations/print-view.html"):
    location = get_object_or_404(Location, pk=id)

    if has_view_perm(request.user,'locations.view_location',location):
        EventLog.objects.log(instance=location)

        return render_to_resp(request=request, template_name=template_name,
            context={'location': location})
    else:
        raise Http403


@is_enabled('locations')
@login_required
def edit(request, id, form_class=LocationForm, template_name="locations/edit.html"):
    location = get_object_or_404(Location, pk=id)

    if has_perm(request.user,'locations.change_location',location):
        if request.method == "POST":
            form = form_class(request.POST, request.FILES, instance=location, user=request.user)
            if form.is_valid():
                location = form.save(commit=False)

                # update all permissions and save the model
                location = update_perms_and_save(request, form, location)

                if 'photo_upload' in form.cleaned_data:
                    photo = form.cleaned_data['photo_upload']
                    if photo:
                        location.save(photo=photo)
                msg_string = 'Successfully updated %s' % location
                messages.add_message(request, messages.SUCCESS, _(msg_string))

                return HttpResponseRedirect(reverse('location', args=[location.slug]))
        else:
            form = form_class(instance=location, user=request.user)

        return render_to_resp(request=request, template_name=template_name,
            context={'location': location, 'form':form})
    else:
        raise Http403


@is_enabled('locations')
@login_required
def add(request, form_class=LocationForm, template_name="locations/add.html"):
    if has_perm(request.user,'locations.add_location'):
        if request.method == "POST":
            form = form_class(request.POST, request.FILES, user=request.user)
            if form.is_valid():
                location = form.save(commit=False)

                # update all permissions and save the model
                location = update_perms_and_save(request, form, location)

                if 'photo_upload' in form.cleaned_data:
                    photo = form.cleaned_data['photo_upload']
                    if photo:
                        location.save(photo=photo)
                msg_string = 'Successfully added %s' % location
                messages.add_message(request, messages.SUCCESS, _(msg_string))

                return HttpResponseRedirect(reverse('location', args=[location.slug]))
        else:
            form = form_class(user=request.user)

        return render_to_resp(request=request, template_name=template_name,
            context={'form':form})
    else:
        raise Http403


@is_enabled('locations')
@login_required
def delete(request, id, template_name="locations/delete.html"):
    location = get_object_or_404(Location, pk=id)

    if has_perm(request.user,'locations.delete_location'):
        if request.method == "POST":
            msg_string = 'Successfully deleted %s' % location
            messages.add_message(request, messages.SUCCESS, _(msg_string))
            location.delete()

            return HttpResponseRedirect(reverse('location.search'))

        return render_to_resp(request=request, template_name=template_name,
            context={'location': location})
    else:
        raise Http403


@is_enabled('locations')
@login_required
@admin_required
@password_required
def locations_import_upload(request, template_name='locations/import-upload-file.html'):
    """
    This is the upload view for the location imports.
    This will upload the location import file and then redirect the user
    to the import mapping/preview page of the import file
    """
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():

            locport = LocationImport.objects.create(creator=request.user)
            csv = File.objects.save_files_for_instance(request, locport)[0]
            file_path = str(csv.file.name)
            import_valid, import_errs = is_import_valid(file_path)

            if not import_valid:
                for err in import_errs:
                    messages.add_message(request, messages.ERROR, err)
                locport.delete()
                return redirect('locations_import_upload_file')
            EventLog.objects.log()
            # reset the password_promt session
            del request.session['password_promt']
            return redirect('locations_import_preview', locport.id)
    else:
        form = UploadForm()

    return render_to_resp(request=request, template_name=template_name, context={
            'form': form,
            'now': datetime.now(),
        })


@login_required
@admin_required
def locations_import_preview(request, id, template_name='locations/import-map-fields.html'):
    """
    This will generate a form based on the uploaded CSV for field mapping.
    A preview will be generated based on the mapping given.
    """
    locport = get_object_or_404(LocationImport, pk=id)

    if request.method == 'POST':
        form = ImportMapForm(request.POST, locport=locport)

        if form.is_valid():
            # Show the user a preview based on the mapping
            cleaned_data = form.cleaned_data
            #file_path = os.path.join(settings.MEDIA_ROOT, locport.get_file().file.name)
            file_path = locport.get_file().file.name
            locations, stats = parse_locs_from_csv(file_path, cleaned_data)

            # return the form to use it for the confirm view
            template_name = 'locations/import-preview.html'
            return render_to_resp(request=request, template_name=template_name, context={
                'locations': locations,
                'stats': stats,
                'locport': locport,
                'form': form,
                'now': datetime.now(),
            })

    else:
        form = ImportMapForm(locport=locport)

    return render_to_resp(request=request, template_name=template_name, context={
        'form': form,
        'locport': locport,
        'now': datetime.now(),
        })


@login_required
@admin_required
def locations_import_confirm(request, id, template_name='locations/import-confirm.html'):
    """
    Confirm the locations import and continue with the process.
    This can only be accessed via a hidden post form from the preview page.
    That will hold the original mappings selected by the user.
    """
    locport = get_object_or_404(LocationImport, pk=id)

    if request.method == "POST":
        form = ImportMapForm(request.POST, locport=locport)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            file_path = str(locport.get_file().file.name)

            if not settings.CELERY_IS_ACTIVE:
                # if celery server is not present
                # evaluate the result and render the results page
                result = ImportLocationsTask()
                locations, stats = result.run(request.user, file_path, cleaned_data)
                return render_to_resp(request=request, template_name=template_name, context={
                    'locations': locations,
                    'stats': stats,
                    'now': datetime.now(),
                })
            else:
                result = ImportLocationsTask.delay(request.user, file_path, cleaned_data)

            return redirect('locations_import_status', result.task_id)
    else:
        return redirect('locations_import_preview', locport.id)


@login_required
@admin_required
def locations_import_status(request, task_id, template_name='locations/import-confirm.html'):
    """
    Checks if a location import is completed.
    """
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        #tasks database entries are not created at once.
        task = None

    if task and task.status == "SUCCESS":

        locations, stats = task.result

        return render_to_resp(request=request, template_name=template_name, context={
            'locations': locations,
            'stats':stats,
            'now': datetime.now(),
        })
    else:
        return render_to_resp(request=request, template_name='memberships/import-status.html', context={
            'task': task,
            'now': datetime.now(),
        })


@is_enabled('locations')
@login_required
def export(request, template_name="locations/export.html"):
    """Export Locations"""

    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        # initilize initial values
        fields = [
            'guid',
            'location_name',
            'description',
            'contact',
            'address',
            'address2',
            'city',
            'state',
            'zipcode',
            'country',
            'phone',
            'fax',
            'email',
            'website',
            'latitude',
            'longitude',
            'hq',
            'entity',
        ]

        export_id = run_export_task('locations', 'location', fields)
        EventLog.objects.log()
        return redirect('export.status', export_id)

    return render_to_resp(request=request, template_name=template_name, context={
    })


@is_enabled('locations')
@admin_required
@login_required
def download_location_upload_template(request):
    file_ext = '.csv'
    filename = "import-locations.csv"

    import_field_list = [
        'Location Name',
        'Description',
        'Contact',
        'Address',
        'Address 2',
        'City',
        'State',
        'Zipcode',
        'Country',
        'Phone',
        'Fax',
        'Email',
        'Website',
        'Latitude',
        'Longitude',
        'Headquarters',
    ]
    data_row_list = []

    return render_excel(filename, import_field_list, data_row_list, file_ext)
