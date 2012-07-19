from django.forms.widgets import MultiWidget, DateInput, TextInput
from time import strftime

class SplitDateTimeWidget(MultiWidget):
    def __init__(self, attrs={}, date_format=None, time_format=None):
        if 'date_class' in attrs:
            date_class = attrs['date_class']
            del attrs['date_class']
        else:
            date_class = 'datepicker'
        
        if 'time_class' in attrs:
            time_class = attrs['time_class'] 
            del attrs['time_class']
        else:
            time_class = 'timepicker'
            
        time_attrs = attrs.copy()
        time_attrs['class'] = time_class
        date_attrs = attrs.copy()
        date_attrs['class'] = date_class

        widgets = (DateInput(attrs=date_attrs, format=date_format),
                   TextInput(attrs=time_attrs))

        super(SplitDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            date = strftime("%Y-%m-%d", value.timetuple())
            time = strftime("%I:%M %p", value.timetuple())
            return (date, time)
        else:
            return (None, None)

    def format_output(self, rendered_widgets):
        """
        Given a list of rendered widgets (as strings), it inserts an HTML
        linebreak between them.

        Returns a Unicode string representing the HTML for the whole lot.
        """
        return "%s&nbsp;%s" % (rendered_widgets[0], rendered_widgets[1])