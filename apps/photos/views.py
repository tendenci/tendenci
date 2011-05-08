import os
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.contrib import messages
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet

from base.http import Http403
from perms.utils import has_perm, update_perms_and_save
from event_logs.models import EventLog

#from photologue.models import *
from photos.utils import dynamic_image
from photos.search_indexes import PhotoSetIndex
from photos.models import Image, Pool, PhotoSet, AlbumCover
from photos.forms import PhotoUploadForm, PhotoEditForm, PhotoSetAddForm, PhotoSetEditForm


def details(request, id, set_id=0, template_name="photos/details.html"):
    """ show the photo details """
    photo = get_object_or_404(Image, id=id)
    set_id = int(set_id)

    # permissions
    if not has_perm(request.user,'photologue.view_photo',photo):
        raise Http403

    # if not public
    if not photo.is_public:
        # if no permission; raise 404 exception
        if not photo.check_perm(request.user,'photos.view_image'):
            raise Http404
    
    photo_url = photo.get_large_url()

    is_me = (photo.member == request.user)
    
    return render_to_response(template_name, {
        "photo": photo,
        "photo_url": photo_url,
        "photo_set_id": set_id,
        "id": photo.id,
        "set_id": set_id,
        "is_me": is_me,
    }, context_instance=RequestContext(request))

def photo(request, id, set_id=0, template_name="photos/details.html"):
    """ photo details """

    # check photo set permissions first
    photo_set_sqs = PhotoSet.objects.search('id:%s' % set_id, user=request.user)
    if not photo_set_sqs:
        raise Http403

    try:
        sqs = Image.objects.search('id:%s' % id, user=request.user)
        photo = sqs.best_match().object
    except:
        # can't tell if they're denied
        # or the image does not exist
        # i assume does not exist
        raise Http404

    EventLog.objects.log(**{
        'event_id' : 990500,
        'event_data': '%s (%d) viewed by %s' % (photo._meta.object_name, photo.pk, request.user),
        'description': '%s viewed' % photo._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': photo,
    })

    # default prev/next URL
    photo_prev_url = photo_next_url = ''

    if set_id:
        photo_set = get_object_or_404(PhotoSet, id=set_id)
        photo_prev = photo.get_prev(set=set_id)
        photo_next = photo.get_next(set=set_id)            

        if photo_prev: photo_prev_url = reverse("photo", args= [photo_prev.id, set_id])
        if photo_next: photo_next_url = reverse("photo", args= [photo_next.id, set_id])

        photo_sets = list(photo.photoset.all())
        if photo_set in photo_sets:
            photo_sets.remove(photo_set)
            photo_sets.insert(0, photo_set)
        else:
            set_id = 0
    else:
        photo_prev = photo.get_prev()
        photo_next = photo.get_next()

        if photo_prev: photo_prev_url = reverse("photo", args= [photo_prev.id])
        if photo_next: photo_next_url = reverse("photo", args= [photo_next.id])  

        photo_sets = photo.photoset.all()

    # "is me" variable
    is_me = photo.member == request.user
    
    return render_to_response(template_name, {
        "photo_prev_url": photo_prev_url,
        "photo_next_url": photo_next_url,
        "photo": photo,
        "photo_sets": photo_sets,
        "photo_set_id": set_id,
        "id": id,
        "set_id": set_id,
        "is_me": is_me,
    }, context_instance=RequestContext(request))

def photo_size(request, id=None, size=None, crop=False):
    """
    Renders image and returns response
    Does not use template
    Saves resized image within cache system
    Returns 404 if if image rendering fails
    """

    if id and size:
        photo = get_object_or_404(Image, id=id)
        size = [int(s) for s in size.split('x')]

    # check permissions
    if not has_perm(request.user,'photologue.view_photo',photo):
        raise Http403

    if crop: crop = True

    # gets resized image from cache or rebuild
    image = dynamic_image(photo, size, crop)

    # if image not rendered; quit
    if not image: raise Http404

    response = HttpResponse(mimetype='image/jpeg')
    response['Content-Disposition'] = 'filename=%s'% photo.image.file.name
    image.save(response, "JPEG", quality=100)

    return response


@login_required
def memberphotos(request, username, template_name="photos/memberphotos.html", group_slug=None, bridge=None):
    """ Get the members photos and display them """
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    user = get_object_or_404(User, username=username)
    
    photos = Image.objects.filter(
        member__username = username,
        is_public = True
    )
    
    if group:
        photos = group.content_objects(photos, join="pool")
    else:
        photos = photos.filter(pool__object_id=None)
    
    photos = photos.order_by("-date_added")
    
    return render_to_response(template_name, {
        "group": group,
        "photos": photos,
    }, context_instance=RequestContext(request))


@login_required
def edit(request, id, set_id=0, form_class=PhotoEditForm, template_name="photos/edit.html"):
    """ edit photo view """

    # get photo
    photo = get_object_or_404(Image, id=id)
    set_id = int(set_id)

    # permissions
    if not has_perm(request.user,'photologue.change_photo',photo):
        raise Http403

    # get available photo sets
    photo_sets = PhotoSet.objects.all()

    if request.method == "POST":
        if photo.member != request.user: # no permission
            request.user.message_set.create(message="You can't edit photos that aren't yours")
            return HttpResponseRedirect(reverse('photo', args=(photo.id, set_id)))
        if request.POST["action"] == "update":
            form = form_class(request.POST, instance=photo, user=request.user)
            if form.is_valid():
                photo = form.save(commit=False)

                # update all permissions and save the model
                photo = update_perms_and_save(request, form, photo)

                log_defaults = {
                    'event_id' : 990200,
                    'event_data': '%s (%d) edited by %s' % (photo._meta.object_name, photo.pk, request.user),
                    'description': '%s edited' % photo._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': photo,
                }
                EventLog.objects.log(**log_defaults)

                request.user.message_set.create(message=_("Successfully updated photo '%s'") % photo.title)
                return HttpResponseRedirect(reverse("photo", kwargs={"id": photo.id, "set_id": set_id}))
        else:
            form = form_class(instance=photo, user=request.user)

    else:
        form = form_class(instance=photo, user=request.user)

    return render_to_response(template_name, {
        "photo_form": form,
        "photo": photo,
        "photo_sets": photo_sets,
        "id": photo.id, 
        "set_id": set_id,
    }, context_instance=RequestContext(request))

@login_required
def delete(request, id, set_id=0):
    """ delete photo """
    photo = get_object_or_404(Image, id=id)

    # permissions
    if not has_perm(request.user,'photologue.delete_photo',photo):
        raise Http403

    if request.method == "POST":
        request.user.message_set.create(message=_("Successfully deleted photo '%s'") % photo.title)
        log_defaults = {
            'event_id' : 990300,
            'event_data': '%s (%d) deleted by %s' % (photo._meta.object_name, photo.pk, request.user),
            'description': '%s deleted' % photo._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': photo,
        }
        EventLog.objects.log(**log_defaults)

        photo.delete()

        return HttpResponseRedirect(reverse("photoset_details", args=[set_id]))

    return render_to_response("photos/delete.html", {
        "photo": photo,
    }, context_instance=RequestContext(request))

@login_required
def photoset_add(request, form_class=PhotoSetAddForm, template_name="photos/photo-set/add.html"):
    """ Add a photo set """

    # if no permission; permission exception
    if not has_perm(request.user,'photos.add_photoset'):
        raise Http403

    if request.method == "POST":
        if request.POST["action"] == "add":

            form = form_class(request.POST, user=request.user)
            if form.is_valid():
                photo_set = form.save(commit=False)

                photo_set.author = request.user

                # update all permissions and save the model
                photo_set = update_perms_and_save(request, form, photo_set)

                log_defaults = {
                    'event_id' : 991100,
                    'event_data': '%s (%d) added by %s' % (photo_set._meta.object_name, photo_set.pk, request.user),
                    'description': '%s added' % photo_set._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': photo_set,
                }
                EventLog.objects.log(**log_defaults) 

                request.user.message_set.create(message=_("Successfully added photo set!") + '')
                return HttpResponseRedirect(reverse('photos_batch_add', kwargs={'photoset_id':photo_set.id}))
    else:
        form = form_class(user=request.user)

    return render_to_response(template_name, {
        "photoset_form": form,
    }, context_instance=RequestContext(request))


@login_required
def photoset_edit(request, id, form_class=PhotoSetEditForm, template_name="photos/photo-set/edit.html"):
    photo_set = get_object_or_404(PhotoSet, id=id)

    # if no permission; permission exception
    if not has_perm(request.user,'photos.change_photoset',photo_set):
        raise Http403

    if request.method == "POST":
        if request.POST["action"] == "edit":
            form = form_class(request.POST, instance=photo_set, user=request.user)
            if form.is_valid():
                photo_set = form.save(commit=False)

                # update all permissions and save the model
                photo_set = update_perms_and_save(request, form, photo_set)

                request.user.message_set.create(message=_("Successfully updated photo set! ") + '')

                log_defaults = {
                    'event_id' : 991200,
                    'event_data': '%s (%d) edited by %s' % (photo_set._meta.object_name, photo_set.pk, request.user),
                    'description': '%s edited' % photo_set._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': photo_set,
                }
                EventLog.objects.log(**log_defaults)

                return HttpResponseRedirect(reverse('photoset_details', args=[photo_set.id]))
    else:
        form = form_class(instance=photo_set, user=request.user)

    return render_to_response(template_name, {
        "photoset_form": form,
    }, context_instance=RequestContext(request))

@login_required
def photoset_delete(request, id, template_name="photos/photo_set/delete.html"):
    photo_set = get_object_or_404(PhotoSet, id=id)

    # if no permission; permission exception
    if not has_perm(request.user,'photos.delete_photoset',photo_set):
        raise Http403

    log_defaults = {
        'event_id' : 991300,
        'event_data': '%s (%d) deleted by %s' % (photo_set._meta.object_name, photo_set.pk, request.user),
        'description': '%s deleted' % photo_set._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': photo_set,
    }
    EventLog.objects.log(**log_defaults)

    photo_set.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', None))

def photoset_view_latest(request, template_name="photos/photo-set/latest.html"):
    """ View latest photo set """

    query = request.GET.get('q', None)
    photo_sets = PhotoSet.objects.search(query, user=request.user)
    photo_sets = photo_sets.order_by('-update_dt')

    log_defaults = {
        'event_id' : 991400,
        'event_data': '%s searched by %s' % ('PhotoSet', request.user),
        'description': '%s searched' % 'PhotoSet',
        'user': request.user,
        'request': request,
        'source': 'photos'
    }
    EventLog.objects.log(**log_defaults)
        
    return render_to_response(template_name, {"photo_sets": photo_sets}, 
        context_instance=RequestContext(request))

@login_required
def photoset_view_yours(request, template_name="photos/photo-set/yours.html"):
    """ View your photo set """
    photo_sets = PhotoSet.objects.all()
    return render_to_response(template_name, {
        "photo_sets": photo_sets,
    }, context_instance=RequestContext(request))

@login_required
def photos_batch_add(request, photoset_id=0):
    """
    params: request, photoset_id
    returns: HttpResponse

    on flash request:
        photoset_id is passed via request.POST
        and received as type unicode; i convert to type integer
    on http request:
        photoset_id is passed via url
    """

    # photoset permission required to add photos
    if not has_perm(request.user,'photos.add_photoset'):
        raise Http403

    if request.method == 'POST':

        for field_name in request.FILES:
            uploaded_file = request.FILES[field_name]

            # use file to create title; remove extension
            filename, extension = os.path.splitext(uploaded_file.name)
            request.POST.update({'title': filename, })

            # photoset_id set in swfupload
            photoset_id = int(request.POST["photoset_id"])

            request.POST.update({
                'owner': request.user.id,
                'owner_username': str(request.user),
                'creator_username': str(request.user),
                'status': True,
                'status_detail': 'active',
            })
            photo_form = PhotoUploadForm(request.POST, request.FILES, user=request.user)

            if photo_form.is_valid():
                # save photo
                photo = photo_form.save(commit=False)
                photo.creator = request.user
                photo.member = request.user
                photo.safetylevel = 3
                photo.allow_anonymous_view = True

                # update all permissions and save the model
                photo = update_perms_and_save(request, photo_form, photo)

                EventLog.objects.log(**{
                    'event_id' : 990100,
                    'event_data': '%s (%d) added by %s' % (photo._meta.object_name, photo.pk, request.user),
                    'description': '%s added' % photo._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': photo,
                }) 

                # add to photo set if photo set is specified
                if photoset_id:
                    photo_set = get_object_or_404(PhotoSet, id=photoset_id)
                    photo_set.image_set.add(photo)

                # serialize queryset
                data = serializers.serialize("json", Image.objects.filter(id=photo.id))
    
                # returning a response of "ok" (flash likes this)
                # response is for flash, not humans
                return HttpResponse(data, mimetype="text/plain")
            else:
                return HttpResponse("photo is not valid", mimetype="text/plain")

    else:

        if not photoset_id:
            HttpResponseRedirect(reverse('photoset_latest'))

        photo_set = get_object_or_404(PhotoSet, id=photoset_id)

        # show the upload UI
        return render_to_response('photos/batch-add.html', {
            "photoset_id":photoset_id,
            "photo_set": photo_set,
             },
            context_instance=RequestContext(request))

def photos_batch_edit(request, photoset_id=0, template_name="photos/batch-edit.html"):
    """ change multiple photos with one "save button" click """
    photo_set = get_object_or_404(PhotoSet, id=photoset_id)
    if not photo_set.check_perm(request.user, 'photos.change_photoset'):
        raise Http403

    PhotoFormSet = modelformset_factory(
        Image,
        can_delete=True,
        exclude=(
            'title_slug',
            'creator_username',
            'owner_username',
            'photoset',
            'is_public',
            'owner',
            'safetylevel',
            'allow_anonymous_view',
            'status',
            'status_detail',
        ),
        extra=0
    )

    if request.method == "POST":
        photo_formset = PhotoFormSet(request.POST)
        if photo_formset.is_valid():
            photo_formset.save()

            # event logging
            for photo, changed in photo_formset.changed_objects:

                EventLog.objects.log(**{
                    'event_id' : 990200,
                    'event_data': 'photo (%s) edited by %s' % (photo.pk, request.user),
                    'description': '%s edited' % photo._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': photo,
                })
            
            #set album cover if specified
            chosen_cover_id = request.POST.get('album_cover', None)
            print "chosen", chosen_cover_id
            if chosen_cover_id:
                #validate chosen cover
                valid_cover = True
                try:
                    chosen_cover = photo_set.image_set.get(id=chosen_cover_id)
                except Image.DoesNotExist:
                    valid_cover = False
                if valid_cover:
                    try:
                        cover = AlbumCover.objects.get(photoset=photo_set)
                    except AlbumCover.DoesNotExist:
                        cover = AlbumCover(photoset=photo_set)
                    cover.photo = chosen_cover
                    cover.save()
            
            messages.add_message(request, messages.INFO, 'Photo changes saved')
            return HttpResponseRedirect(reverse('photoset_details', args=(photoset_id,)))  

    else:
        # if not request.method == POST

        # i would like to use the search index here; but it appears that
        # the formset class only accepts a queryset; not a searchqueryset or list
        photo_qs = Image.objects.filter(photoset=photo_set).order_by("-update_dt")
        photo_formset = PhotoFormSet(queryset=photo_qs)

    return render_to_response(template_name, {
        "photo_formset": photo_formset,
        "photo_set": photo_set,
    }, context_instance=RequestContext(request))


def photoset_details(request, id, template_name="photos/photo-set/details.html"):
    """ View photos in photo set """

    # check photo-set permissions
    # ---> why use search? wouldn't a direct query be faster?
    # ---> this also does not take into account the actual user permissions.
    photo_sets = PhotoSet.objects.search('id:%s' % id, user=request.user)
    if not photo_sets:
        raise Http404
    photo_set = photo_sets.best_match().object
    photos = Image.objects.search('set_id:%s' % photo_set.pk, user=request.user).order_by("-update_dt")
    
    # code for non search dependent detail view
    # --> currently incompatible with the template used
    # photo_set = get_object_or_404(PhotoSet, id=id)
    # if not has_perm(request.user,'photos.change_photoset',photo_set):
    #     raise Http403
    # photos = photo_set.image_set.all()

    EventLog.objects.log(**{
        'event_id' : 991500,
        'event_data': '%s (%d) viewed by %s' % (photo_set._meta.object_name, photo_set.pk, request.user),
        'description': '%s viewed' % photo_set._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': photo_set,
    })

    return render_to_response(template_name, {
        "photos": photos,
        "photo_set": photo_set,
    }, context_instance=RequestContext(request))
