from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import datetime
from django.utils.text import slugify

class Theme(models.Model):
    title = models.CharField(max_length=255,unique=True)
    slug = models.SlugField(max_length=255,unique=True,editable=False)
    description = models.TextField(null=True,blank=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super(Theme, self).save(*args, **kwargs)
        if self.slug is None or self.slug == "":
            self.slug = '%s-%i' % (
                slugify(self.title), self.id
            )
        super(Theme, self).save(*args, **kwargs)

class Process(models.Model):
    title = models.CharField(max_length=255,unique=True)
    slug = models.SlugField(max_length=255,unique=True,editable=False)
    description = models.TextField(null=True,blank=True)
    start = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    end = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    theme = models.ManyToManyField(Theme, related_name="processes", related_query_name="process",blank=True)
    
    class Meta:
        ordering = ['start','title']
        verbose_name_plural = "processes"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super(Process, self).save(*args, **kwargs)
        if self.slug is None or self.slug == "":
            self.slug = '%s-%i' % (
                slugify(self.title), self.id
            )
        super(Process, self).save(*args, **kwargs)
    
class Tag(models.Model):
    title = models.CharField(max_length=255,unique=True)
    slug = models.SlugField(max_length=255,unique=True,editable=False)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super(Tag, self).save(*args, **kwargs)
        if self.slug is None or self.slug == "":
            self.slug = '%s-%i' % (
                slugify(self.title), self.id
            )
        super(Tag, self).save(*args, **kwargs)

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True,blank=True)
    location = models.CharField(max_length=255,null=True,blank=True)
    slug = models.SlugField(unique=True,max_length=255, null=True, blank=True,editable=False)
    url = models.URLField(unique=True,max_length=255, null=True, blank=True,editable=False)
    start = models.DateField(auto_now=False, auto_now_add=False)
    end = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, auto_now_add=False)
    holder = models.ForeignKey(User, null=True, blank=True,editable=True)
    tag = models.ManyToManyField(Tag, related_name="events", related_query_name="event",blank=True)
    process = models.ManyToManyField(Process, related_name="events", related_query_name="event",blank=True)
    priority = models.IntegerField(blank=True,null=True)
    LEVEL_CHOICES = (
        ('BG','Background'),
        ('LC','Localized'),
        ('PT','Participating'),
    )
    level = models.CharField(max_length=2,choices=LEVEL_CHOICES,default='BG')
    lead = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    follow = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    
    
    class Meta:
        ordering = ['start','title']
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("cal.views.event",args=[self.slug])
    
    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)
        date = self.start
        if self.slug is None or self.slug == "":
            self.slug = '%s-%i%i%i%i' % (
                slugify(self.title), date.year, date.month, date.day, self.id
            )
        self.url = reverse("cal.views.event",args=[self.slug])
        super(Event, self).save(*args, **kwargs)
        
class Activity(models.Model):
    title = models.CharField(max_length=255,unique=True)
    start = models.DateField(auto_now=False, auto_now_add=False)
    description = models.TextField(null=True,blank=True)
    end = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    holder = models.ForeignKey(User, null=True, blank=True,editable=True)
    event = models.ForeignKey(Event,related_name="activities",related_query_name="activity",blank=True,null=True)
    
    class Meta:
        ordering = ['start','title']
        verbose_name_plural = "activities"
    
    def __str__(self):
        return self.title