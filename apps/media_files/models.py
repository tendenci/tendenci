# django
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

class MediaFile(models.Model):

    file = models.FileField(upload_to='uploads/%m/%Y')
    name = models.CharField(max_length=2000)
    description = models.TextField(blank=True)
    created_dt = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(auto_now=True, auto_now_add=True)
    is_public = models.BooleanField(_('public'), default=True)
    user = models.ForeignKey(User, blank=True, null=True)
    application = models.ForeignKey(ContentType, blank=True, null=True)
    application_instance_id = models.IntegerField(blank=True, null=True)
    
    class Meta:
        verbose_name = _('media')
        verbose_name_plural = _('media')

    def delete(self):
        import os

        # get file and extension
        file, ext = os.path.splitext(self.file.path)

        try: # remove copies
            os.remove(file + '_thumbnail' + ext)
            os.remove(file + '_medium' + ext)
            os.remove(file + '_large' + ext)
        except: pass

        super(MediaFile, self).delete()
        
           
    def __unicode__(self):
        return self.name

    def copy_image(self, size, hook=None, crop=False, crop_from='center'):
        import Image
        import os

        # make image instance
        try: im = Image.open(self.file.path)
        except IOError: return None

        # get file and extension
        file, ext = os.path.splitext(self.file.path)

        # make default hook; string to append to filename
        if not hook: hook = '-' + str(new_width) + 'x' + str(new_height)

        new_file_path = file + hook + ext

        # get current dimensions and new dimensions
        cur_width, cur_height = im.size
        new_width, new_height = size

        if crop:
            ratio = max(float(new_width)/cur_width,float(new_height)/cur_height)
            x = (cur_width * ratio)
            y = (cur_height * ratio)
            xd = abs(new_width - x)
            yd = abs(new_height - y)
            x_diff = int(xd / 2)
            y_diff = int(yd / 2)

            if crop_from == 'top':
                box = (int(x_diff), 0, int(x_diff+new_width), new_height)
            elif crop_from == 'left':
                box = (0, int(y_diff), new_width, int(y_diff+new_height))
            elif crop_from == 'bottom':
                box = (int(x_diff), int(yd), int(x_diff+new_width), int(y)) # y - yd = new_height
            elif crop_from == 'right':
                box = (int(xd), int(y_diff), int(x), int(y_diff+new_height)) # x - xd = new_width
            else:
                box = (int(x_diff), int(y_diff), int(x_diff+new_width), int(y_diff+new_height))

            # resize and save new image
            im = im.resize((int(x), int(y)), Image.ANTIALIAS).crop(box)
        else:

            if not new_width == 0 and not new_height == 0:
                ratio = min(float(new_width)/cur_width,
                            float(new_height)/cur_height)
            else:
                if new_width == 0:
                    ratio = float(new_height)/cur_height
                else:
                    ratio = float(new_width)/cur_width
            new_dimensions = (int(round(cur_width*ratio)),
                              int(round(cur_height*ratio)))

            # resize and save new image
            im = im.resize(new_dimensions, Image.ANTIALIAS)
            
        im.save(new_file_path)
        os.system('chmod 775 ' + new_file_path)
        return im
