from django import forms
from actions.models import Action

DAYS_CHOICES = ((1,'1'), (3,'3'), (5,'5'), (7,'7'),
                (14,'14'), (30,'30'), (60,'60'), (90,'90'),
                (120,'120'), (0,'ALL'),
                )
INCLUDE_CHOICES = (('1', 'Include'),('0', 'Skip'),)

class NewsletterAddForm(forms.ModelForm):
    subject = forms.CharField(max_length=250,
                              widget=forms.TextInput(attrs={'size':'60',
                                                            'class': 'newsletter-subject'}))
    personalize_subject_first_name = forms.BooleanField()
    personalize_subject_last_name = forms.BooleanField()
    include_login = forms.BooleanField()
    jump_links = forms.ChoiceField(initial='1', choices=INCLUDE_CHOICES)
    events =  forms.ChoiceField(initial='1', choices=INCLUDE_CHOICES)
    event_start_dt = forms.DateField(required=False)
    event_end_dt = forms.DateField(required=False)
    articles = forms.ChoiceField(initial='1', choices=INCLUDE_CHOICES)
    articles_days = forms.ChoiceField(initial=60, choices=DAYS_CHOICES)
    news = forms.ChoiceField(initial='1', choices=INCLUDE_CHOICES)
    news_days = forms.ChoiceField(initial=30, choices=DAYS_CHOICES)
    jobs = forms.ChoiceField(initial='1', choices=INCLUDE_CHOICES)
    jobs_days = forms.ChoiceField(initial=30, choices=DAYS_CHOICES)
    pages = forms.ChoiceField(initial='0', choices=INCLUDE_CHOICES)
    pages_days = forms.ChoiceField(initial=7, choices=DAYS_CHOICES)
    template_name = forms.CharField(max_length=150)
    format = forms.CharField(widget=forms.RadioSelect(choices=(('detailed', 'Detailed - original format'), 
                                                              ('simplified', 'Simplified - removes AUTHOR, '+\
                                                               'POSTED BY, RELEASES DATE, etc from the detailed format'),)), 
                                                               initial='detailed', )
    
    class Meta:
        model = Action
        fields = ('member_only',
                  'group',
                  'send_to_email2',
                  'subject',
                  'personalize_subject_first_name',
                  'personalize_subject_last_name',
                  'include_login',
                  'jump_links',
                  'events',
                  'event_start_dt',
                  'event_end_dt',
                  'articles',
                  'articles_days',
                  'news',
                  'news_days',
                  'jobs',
                  'jobs_days',
                  'pages',
                  'pages_days',
                  'template_name',
                  'format',
                  )