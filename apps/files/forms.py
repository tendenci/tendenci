from django import forms
from files.models import File
from perms.forms import TendenciBaseForm

class FileForm(TendenciBaseForm):
    class Meta:
        model = File

        fields = (
            'file',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
        )

        fieldsets = [('', {
                      'fields': ['file'],
                      'legend': ''
                      }),

                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),

                     ('Administrator Only', {
                      'fields': ['status',
                                 'status_detail'], 
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        else:
            self.user = None
        super(FileForm, self).__init__(*args, **kwargs)

class MostViewedForm(forms.Form):
  """
  Takes in the date range and files type you're 
  searching for and returns back a result list.
  """

  TYPES = (
    ('all', 'All File Types'),
    ('pdf', 'PDF Documents'),
    ('slides', 'Slides'),
    ('spreadsheet', 'Spreadsheets'),
    ('text', 'Text Documents'),
    ('zip', 'Zip Files'),
  )

  start_dt = forms.DateField(label='Start')
  end_dt = forms.DateField(label='End')
  file_type = forms.ChoiceField(label='File Type', choices=TYPES)

  def __init__(self, *args, **kwargs):
    super(MostViewedForm, self).__init__(*args, **kwargs)
    self.fields['file_type'].widget.attrs['class'] = 'btn'
