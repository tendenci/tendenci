from django.contrib.auth.models import User
from django.template.loader import get_template
#from django.http import HttpResponse

from xhtml2pdf import pisa

from tendenci.apps.trainings.models import Transcript, OutsideSchool, TeachingActivity
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.files.models import File


def user_transcripts(user, location_type='online',
                     online_courses=None,
                     onsite_courses=None):
    if isinstance(user, User):
        if location_type in ['online', 'onsite']:
            if not any([online_courses, onsite_courses]):
                return None
            transcripts = Transcript.objects.filter(
                    location_type=location_type,
                    user=user)
            if location_type == 'online' and online_courses:
                transcripts = transcripts.filter(course_id__in=online_courses)
            if location_type == 'onsite' and onsite_courses:
                transcripts = transcripts.filter(course_id__in=onsite_courses)

            return transcripts
        if location_type in ['outside']:
            return Transcript.objects.filter(
                    location_type=location_type,
                    user=user)
    return None


def user_outside_schools(user):       
    if isinstance(user, User):
        return OutsideSchool.objects.filter(user=user) 
 
    return None


def user_teaching_activities(user):       
    if isinstance(user, User):
        return TeachingActivity.objects.filter(user=user) 
 
    return None


def generate_transcript_pdf(f, **kwargs):
    """
    Generate transcripts PDF for this customer.
    """
    #customer = kwargs.get('customer')
    template_name = 'trainings/transcript_pdf.html'
    template = get_template(template_name)
    kwargs['for_pdf'] = True
    kwargs['logo_base64_src'] = ''
    logo_file_id = get_setting('module', 'trainings', 'transcriptlogo')
    if logo_file_id:
        [file] = File.objects.filter(id=logo_file_id)[:1] or [None]
        if file:
            kwargs['logo_base64_src'] = f"data:{file.mime_type()};base64,{file.get_binary(size=(180, 100))}"

    html = template.render(context=kwargs)

    pisa.CreatePDF(html, dest=f)
    return f
