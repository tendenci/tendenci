import os.path
from django.db import models
from django.conf import settings

from perms.models import AuditingBaseModel
from stories.managers import StoryManager
from perms.utils import is_admin

# Create your models here.
class Story(AuditingBaseModel):
    guid = models.CharField(max_length=50, unique=False, blank=True)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
    syndicate = models.BooleanField()
    create_dt = models.DateTimeField(auto_now_add=True)
    fullstorylink = models.CharField(max_length=300, blank=True)
    start_dt = models.DateTimeField(null=True, blank=True)
    end_dt = models.DateTimeField(null=True, blank=True)
    ncsortorder = models.IntegerField(null=True, blank=True)
 
    objects = StoryManager()
    
    class Meta:
        permissions = (("view_story","Can view story"),)
        verbose_name_plural = "stories"

    @models.permalink
    def get_absolute_url(self):
        return ("story", [self.pk])

    def __unicode__(self):
        return self.title
    
    # if this story allows view by user2_compare
    def allow_view_by(self, user2_compare):
        boo = False
       
        if is_admin(user2_compare):
            boo = True
        else:
            if self.creator == user2_compare or self.owner == user2_compare:
                if self.status == 1:
                    boo = True
            else:
                if self.status==1 and self.status_detail.lower()=='active':
                    boo = True
            
        return boo
    
    def allow_add_by(self, user2_compare):
        if is_admin(user2_compare):
            return True
        else:
            if user2_compare.has_perm('stories.add_story'):
                return True
        return False
    
    # if this story allows edit by user2_compare
    def allow_edit_by(self, user2_compare):
        if is_admin(user2_compare):
            return True
        else:
            if self.creator == user2_compare or self.owner == user2_compare:
                if self.status == 1:
                    return True
            else:
                if user2_compare.has_perm('stories.change_story', self):
                    return True
        return False
    
    def get_image_url(self):
        imagepath = os.path.join(settings.MEDIA_ROOT, 'stories/'+str(self.id))
        image_name = self.get_latest_image_name(imagepath)
        if image_name <> "":
            image_url = os.path.join(settings.MEDIA_URL, 'stories/'+str(self.id) +'/' + image_name)
        else:
            image_url = ""
        return image_url
    
    # get the latest image name
    def get_latest_image_name(self, images_path):
        latest_image = ""
        if os.path.isdir(images_path):
            image_list = os.listdir(images_path)
            
            if image_list <> []:
                image_full_path_list = [images_path+'/'+image_name for image_name in image_list]
                
                latest_image = image_list[0]
                mtime = os.path.getmtime(image_full_path_list[0])
                
                for i in range(1, len(image_full_path_list)):
                    if mtime < os.path.getmtime(image_full_path_list[i]):
                        latest_image = image_list[i]
                        mtime = os.path.getmtime(image_full_path_list[i])
        return latest_image
        