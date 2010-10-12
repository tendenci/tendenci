from django.db import models


class Post(models.Model):
    """ Simple blog post model"""
    title = models.CharField(max_length=255)
    intro = models.TextField(blank=True)
    body = models.TextField()
    
    def __unicode__(self):
        return self.title

