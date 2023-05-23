from django.db.models.signals import post_save
from tendenci.apps.events.models import Registrant
from tendenci.apps.trainings.models import Transcript, OutsideSchool


def reg_save_transcript(sender, **kwargs):
    """
    Add or update an transcript entry on event registration add or edit.
    """
    from tendenci.apps.trainings.models import Transcript

    registrant = kwargs['instance']
    event = registrant.registration.event
    if all([event.course, registrant.user]):
        [transcript] = Transcript.objects.filter(registrant_id=registrant.id)[:1] or [None]
        if not transcript:
            if registrant.cancel_dt:
                return

            transcript = Transcript(user=registrant.user,
                                    parent_id=registrant.id,
                                    location_type='onsite',
                                    registrant_id=registrant.id,
                                    creator=registrant.registration.creator)
        transcript.school_category = event.course.school_category
        transcript.course = event.course
        if registrant.certification_track:
            transcript.certification_track = registrant.certification_track
        transcript.location_type = event.course.location_type
        transcript.credits = event.course.credits
        transcript.owner = registrant.registration.owner
        if registrant.cancel_dt:
            transcript.status = 'cancelled'
        transcript.save()

   
def outside_school_save_transcript(sender, **kwargs):
    """
    Add or update an transcript entry on outside school add or edit.
    """
    outside_school = kwargs['instance']

    [transcript] = Transcript.objects.filter(
        parent_id=outside_school.id,
        user=outside_school.user,
        location_type='outside')[:1] or [None]
    if not transcript:
        transcript = Transcript(user=outside_school.user,
                                parent_id=outside_school.id,
                                location_type='outside',
                                creator=outside_school.creator)
    
    transcript.school_category = outside_school.school_category
    if outside_school.certification_track:
        transcript.certification_track = outside_school.certification_track
    if outside_school.credits:
        transcript.credits = outside_school.credits
    transcript.owner = outside_school.owner
    transcript.status = outside_school.status_detail

    transcript.save()


def init_signals():
    post_save.connect(reg_save_transcript, sender=Registrant, weak=False)
    post_save.connect(outside_school_save_transcript, sender=OutsideSchool, weak=False)
    