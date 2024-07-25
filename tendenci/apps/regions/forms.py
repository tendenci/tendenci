from django import forms
from django.utils.translation import gettext_lazy as _

from tendenci.apps.regions.models import Region
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.site_settings.utils import get_setting


class RegionForm(TendenciBaseForm):

    invoice_header = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label': Region._meta.app_label,
        'storme_model': Region._meta.model_name.lower()}))
    invoice_footer = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label': Region._meta.app_label,
        'storme_model': Region._meta.model_name.lower()}))
    status_detail = forms.ChoiceField(
        choices=(('active', _('Active')),
                 ('inactive', _('Inactive')),
                 ('pending', _('Pending')),))

    class Meta:
        model = Region
        fields = (
        'region_name',
        'region_code',
        'description',
        'tax_rate',
        'tax_rate_2',
        'tax_label_2',
        'invoice_header',
        'invoice_footer',
        'allow_anonymous_view',
        'user_perms',
        'member_perms',
        'group_perms',
        'status_detail',
        )

    def __init__(self, *args, **kwargs):
        super(RegionForm, self).__init__(*args, **kwargs)

        # if not get_setting('module', 'invoices', 'taxrateuseregions'):
        #     del self.fields['tax_rate']
        #     del self.fields['tax_rate_2']
        #     del self.fields['tax_label_2']
        #     del self.fields['invoice_header']
        #     del self.fields['invoice_footer']
