from geraldo import Report, ReportBand, ObjectValue,\
     Label, landscape
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A5
from django.core.urlresolvers import reverse
from django.utils.html import mark_safe

from django.utils.translation import ugettext_lazy as _
from tendenci.libs.model_report.report import reports, ReportAdmin
from tendenci.libs.model_report.utils import count_column, us_date_format, yesno_format
from tendenci.apps.memberships.models import MembershipDefault, MembershipType
MEMBERSHIPTYPE_DICT = dict((m.id, m.name) for m in MembershipType.objects.all())

class ReportBandNewMems(ReportBand):
    def __init__(self, *args, **kwargs):
        days_ago = kwargs.pop('days_ago')
        super(ReportBandNewMems, self).__init__(*args, **kwargs)

class ReportNewMems(Report):
    title = _("New Memberships")
    author = _("John Smith  Corporation")

    page_size = landscape(A5)

    def __init__(self, *args, **kwargs):
        super(ReportNewMems, self).__init__(*args, **kwargs)

    class band_page_header(ReportBand):
        height = 1.2*cm
        elements = [
                Label(text=_("Name"), top=0.8*cm, left=0*cm),
                Label(text=_("Email"), top=0.8*cm, left=2.5*cm),
                Label(text=_("Type"), top=0.8*cm, left=5.5*cm),
                Label(text=_("Price Paid"), top=0.8*cm, left=11.5*cm),
                Label(text=_("Start Date"), top=0.8*cm, left=14.5*cm),
                Label(text=_("End Date"), top=0.8*cm, left=17.5*cm),
            ]

    class band_detail(ReportBand):
        height = 0.5*cm
        elements = (
                ObjectValue(attribute_name='user', left=0*cm,
                    get_value=lambda instance: instance.user.last_name + ', ' + instance.user.first_name),
                ObjectValue(attribute_name='user', left=2.5*cm,
                    get_value=lambda instance: instance.user.email),
                ObjectValue(attribute_name='membership_type', left=5.5*cm),
                ObjectValue(attribute_name='invoice', left=11.5*cm,
                    get_value=lambda instance: instance.get_invoice().total if instance.get_invoice() else ''),
                #ObjectValue(attribute_name='payment_method', left=15*cm),
                ObjectValue(attribute_name='join_dt', left=14.5*cm,
                    get_value=lambda instance: instance.join_dt.strftime('%b %d, %Y')),
                ObjectValue(attribute_name='expire_dt', left=17.5*cm,
                    get_value=lambda instance: instance.expire_dt.strftime('%b %d, %Y') if instance.expire_dt else ''),
            )

def id_format(value, instance):
    link = reverse('membership.details', args=[value])
    html = "<a href=\"%s\">%s</a>" % (link, value)
    return mark_safe(html)


def membership_type_format(value, instance=None):
    return MEMBERSHIPTYPE_DICT.get(value, value)


class MembershipReport(ReportAdmin):
    # choose a title for your report for h1, title tag and report list
    title = _('Membership Report')

    # specify your model
    model = MembershipDefault

    # fields in the specified model to display in the report table
    fields = [
        'id',
        'user__first_name',
        'user__last_name',
        'user__email',
        'expire_dt',
        'membership_type',
        'status_detail',
    ]

    # fields in the model to show filters for
    list_filter = ('status_detail', 'membership_type',)

    # fields in the model to order results by
    list_order_by = ('create_dt',)

    # fields to group results by
    list_group_by = ('membership_type', 'status_detail')

    # allowed export formats. default is excel and pdf
    exports = ('excel', 'pdf',)

    # type = report for report only, type = chart for report and charts. default is report.
    type = 'chart'
    chart_types = ('pie', 'column')
    list_serie_fields = ('id', )
    list_serie_ops = ('len',)   # count
    # hide the show only totals field
    hide_show_only_totals = True
    
    override_group_value = {
        'membership_type': membership_type_format,
    }

    # override field formats by referencing a function
    override_field_formats = {
        'membership_type': membership_type_format,
        'expire_dt': us_date_format,
        'id': id_format,
    }
    
    base_template_name = ''

   

# register your report with the slug and name
reports.register('memberships', MembershipReport)
