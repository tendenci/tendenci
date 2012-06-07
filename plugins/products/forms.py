import imghdr
from os.path import splitext, basename

from django import forms
from django.utils.translation import ugettext_lazy as _

from products.models import Product, Category, Formulation
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png' 
)

class ProductForm(TendenciBaseForm):
    class Meta:
        model = Product
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    generic_description = forms.CharField(required=True,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'products','storme_model':Product._meta.module_name.lower()}))
    product_features = forms.CharField(required=True,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'products','storme_model':Product._meta.module_name.lower()}))
    product_specs = forms.CharField(required=True,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'products','storme_model':Product._meta.module_name.lower()}))
    photo_upload = forms.FileField(label=_('Photo'), required=False)
    
    def clean_photo_upload(self):
        photo_upload = self.cleaned_data['photo_upload']
        if photo_upload:
            extension = splitext(photo_upload.name)[1]
            
            # check the extension
            if extension.lower() not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The photo must be of jpg, gif, or png image type.')
            
            # check the image header
            image_type = '.%s' % imghdr.what('', photo_upload.read())
            if image_type not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The photo is an invalid image. Try uploading another photo.')

        return photo_upload
    
    def save(self, *args, **kwargs):
        product = super(ProductForm, self).save(*args, **kwargs)
        photo_upload = self.cleaned_data.get('photo_upload')
        print 'photo_upload', photo_upload
        print 'product.pk', product.pk
        if photo_upload and product.pk:
            image = ProductPhoto(
                        creator=product.creator,
                        creator_username=product.creator_username,
                        owner=product.owner,
                        owner_username=product.owner_username
                    )
            image.file.save(photo_upload.name, photo_upload)  # save file row
            image.save()  # save image row
            
            if product.product_image:
                product.product_image.delete()  # delete image and file row
            product.product_image = image
            print 'image', image
            product.save()
        return product


class ProductSearchForm(forms.Form):
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)
    category =  forms.ModelChoiceField(queryset=Category.objects.all(), required=False,)
    formulation = forms.ModelChoiceField(queryset=Formulation.objects.all(), required=False,)
