from jobs.models import JobPricing

def get_duration_choices():
    jps = JobPricing.objects.filter(status=1).order_by('duration')
    
    return [(jp.duration, '%d days after the activation date' % jp.duration) for jp in jps]
        