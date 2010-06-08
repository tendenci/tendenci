# python
import Image as Pil

# django
from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response

# local
from base.cache import IMAGE_PREVIEW_CACHE

def image_preview(request, app_label, model, id,  size):
    """
        Grab all image link within a peice of content
        and generate thumbnails of largest image
    """    
    # get page object; protect size
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model)
        instance = content_type.get_object_for_this_type(id=id)
    except:
        return HttpResponseNotFound("Image not found.", mimetype="text/plain")

    response = cache.get(IMAGE_PREVIEW_CACHE + '.'.join([model, instance.id, size]))
    original_size = size
    
    if not response:
        from base.utils import parse_image_sources, make_image_object_from_url, image_rescale
        
        from pages.models import Page
        from articles.models import Article
        from news.models import News
 
        # set sizes
        size_min = (30,30)
        size_cap = (512,512)
        
        size_tuple = size.split('x')
        if len(size_tuple) == 2: size = int(size_tuple[0]), int(size_tuple[1])
        else: size = int(size), int(size)

        if size > size_cap: size = size_cap
    
        image_urls = []
        
        # siphon image urls; make fake image (starting image)
        if isinstance(instance,Page):
            image_urls = parse_image_sources(instance.content)
            
        if isinstance(instance,Article):
            image_urls = parse_image_sources(instance.content)
                  
        if isinstance(instance,News):
            image_urls = parse_image_sources(instance.content)
                                 
        image = Pil.new('RGBA',size_min)
    
        # find biggest image, dimension-wise
        for image_url in image_urls:
            image_candidate = make_image_object_from_url(image_url)
            if image_candidate:
                if image_candidate.size > image.size:
                    image = image_candidate

        if image.size[1] > size_min[1]:
        # rescale, convert-to true-colors; return response
    
            image = image_rescale(image, size)
            if image.mode != "RGB":
                image = image.convert("RGB")
    
            response = HttpResponse(mimetype='image/jpeg')
            
            image.save(response, "JPEG", quality=100)
            
            cache.set(IMAGE_PREVIEW_CACHE + '.'.join([model, instance.id, size]), response)
            return response
    
        else: # raise http 404 error (returns page not found)
            return HttpResponseNotFound("Image not found.", mimetype="text/plain")
    else:
        return response
    
def custom_error(request, template_name="500.html"):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))    