from django.template import Library
from django.urls import reverse

#from tendenci.apps.perms.utils import has_perm
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.trainings.utils import user_transcripts, user_teaching_activities
from tendenci.apps.files.models import File

register = Library()

@register.inclusion_tag('trainings/includes/show_cert.html')
def show_certification(cert, customer, for_pdf=False):
    num_diamonds, diamonds_credits_earned = 0, 0
    if cert.enable_diamond:
        num_diamonds, diamonds_credits_earned = cert.diamonds_earned(customer)
    return {'cert': cert,
            'customer': customer,
            'num_diamonds': num_diamonds,
            'diamonds_credits_earned': diamonds_credits_earned,
            'for_pdf': for_pdf}
  

@register.simple_tag
def get_transcripts(user, location_type='online',
                    online_courses=None,
                    onsite_courses=None):
    return user_transcripts(user, location_type=location_type,
                            online_courses=online_courses,
                            onsite_courses=onsite_courses)

        
@register.simple_tag
def get_outside_schools(user):
    return user_transcripts(user, location_type='outside')      
    #return user_outside_schools(user)


@register.simple_tag
def get_teaching_activities(user):       
    return user_teaching_activities(user)

@register.simple_tag
def get_diamond_image(num_diamonds, for_pdf=False):
    num_diamonds = int(num_diamonds)      
    file_id = get_setting('module', 'trainings', f"diamondimage{num_diamonds}")
    [file] = File.objects.filter(id=file_id)[:1] or [None]
    if not file:
        return None

    if for_pdf:
        # generate base64 image for PDF, because image url won't work on some servers. 
        return f"data:{file.mime_type()};base64,{file.get_binary()}"
    return reverse('file', args=[file.id])

    