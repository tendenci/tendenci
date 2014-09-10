from django import forms
from django.utils.translation import ugettext as _

class ExportForm(forms.Form):
    class Meta:
        fields = (
            'articles',
            'case_studies',
            'events',
            'jobs',
            'news',
            'pages',
            'resumes',
        )
        fieldsets = [(_('Data To Include'), {
                      'fields': ['articles',
                                 'case_studies',
                                 'events',
                                 'jobs',
                                 'news',
                                 'pages',
                                 'resumes',
                                 ],
                      'legend': ''
                      }),]

    articles = forms.BooleanField(label=_("Articles"), required=False)
    case_studies = forms.BooleanField(label=_("Case Studies"), required=False)
    events = forms.BooleanField(label=_("Events"), required=False)
    jobs = forms.BooleanField(label=_("Jobs"), required=False)
    news = forms.BooleanField(label=_("News"), required=False)
    pages = forms.BooleanField(label=_("Pages"), required=False)
    resumes = forms.BooleanField(label=_("Resumes"), required=False)

    def __init__(self, *args, **kwargs):
        super(ExportForm, self).__init__(*args, **kwargs)
        try:
            import case_studies
        except ImportError:
            self.fields.pop('case_studies')
