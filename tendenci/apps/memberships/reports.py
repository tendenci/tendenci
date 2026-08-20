from django.urls import reverse
from django.utils.safestring import mark_safe

# ReportLab does not support gettext_lazy() translations, so use gettext() instead
from django.utils.translation import gettext as _
from tendenci.libs.model_report.report import reports, ReportAdmin
from tendenci.libs.model_report.utils import us_date_format
from tendenci.apps.memberships.models import MembershipDefault, MembershipType

MEMBERSHIPTYPE_DICT = None

def id_format(value, instance):
    link = reverse('membership.details', args=[value])
    html = "<a href=\"{}\">{}</a>".format(link, value)
    return mark_safe(html)


def membership_type_format(value, instance=None):
    global MEMBERSHIPTYPE_DICT
    if not MEMBERSHIPTYPE_DICT:
        MEMBERSHIPTYPE_DICT = {m.id: m.name for m in MembershipType.objects.all()}
    return MEMBERSHIPTYPE_DICT.get(value, value)

class MembershipReport(ReportAdmin):
    # choose a title for your report for h1, title tag and report list
    title = _('Membership Report')

    # specify your model
    model = MembershipDefault

    # fields in the specified model to display in the report table
    fields = [
        'id',
        'user.first_name',
        'user.last_name',
        'user.email',
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
    list_serie_fields = ('membership_type', 'status_detail')
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
