from django.db import models

class Entity(models.Model):
    """just entity"""
    pass



class Topic(models.Model):
    """Help topic"""
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['title']
    
    def __unicode__(self):
        return self.title


class HelpFile(models.Model):
    """Question/Answer infromation"""
    LEVELS = ('basic', 'intermediate', 'advanced', 'expert')
    LEVEL_CHOICES = [(i,i) for i in LEVELS]
    
    topics = models.ManyToManyField(Topic)
    entity = models.ForeignKey(Entity, null=True, blank=True)
    question = models.TextField()
    answer = models.TextField()
    level = models.CharField(choices=LEVEL_CHOICES, max_length=100)
    is_faq = models.BooleanField()
    is_featured = models.BooleanField()
    is_video = models.BooleanField()
    is_syndicated = models.BooleanField()
    view_totals = models.PositiveIntegerField(default=0)
    
    def __unicode__(self):
        return self.question
    
    def level_is(self):
        "Template helper: {% if file.level_is.basic %}..."
        return dict([i, self.level==i] for i in HelpFile.LEVELS)


class Request(models.Model):
    question = models.TextField()
    
    def __unicode__(self):
        return self.question

    