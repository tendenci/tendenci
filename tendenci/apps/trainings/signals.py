from django.db.models.signals import post_save
from tendenci.apps.events.models import Registrant


def save_transcript(sender, **kwargs):
    from tendenci.apps.trainings.models import Transcript
 
    registrant = kwargs['instance']
    event = registrant.registration.event
    if all([event.course, registrant.user]):
        [transcript] = Transcript.objects.filter(registrant_id=registrant.id)[:1] or [None]
        if not transcript:
            transcript = Transcript(user=registrant.user,
                                    registrant_id=registrant.id,
                                    creator=registrant.registration.creator)
        transcript.school_category = event.course.school_category
        transcript.course = event.course
        transcript.certification_track = registrant.certification_track
        transcript.location_type = event.course.location_type
        transcript.credits = event.course.credits
        transcript.owner = registrant.registration.owner
        transcript.save()


def init_signals():
    post_save.connect(save_transcript, sender=Registrant, weak=False)