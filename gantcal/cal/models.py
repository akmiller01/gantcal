from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from datetime import datetime
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
    purpose = models.TextField(null=True,blank=True)
    attendee = models.ManyToManyField(User,related_name="events",related_query_name="event",blank=True)
    location = models.CharField(max_length=255,null=True,blank=True)
    slug = models.SlugField(unique=True,max_length=255, null=True, blank=True,editable=False)
    start = models.DateField(auto_now=False, auto_now_add=False)
    end = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, auto_now_add=False)
    tag = models.ManyToManyField(Tag, related_name="events", related_query_name="event",blank=True)
    process = models.ManyToManyField(Process, related_name="events", related_query_name="event",blank=True)
    priority = models.IntegerField(blank=True,null=True)
    estimated_cost = models.IntegerField(blank=True,null=True)
    FOCUS_CHOICES = (
        ('BG','Background'),
        ('LC','Localized'),
        ('PT','Participating'),
    )
    focus = models.CharField(max_length=2,choices=FOCUS_CHOICES,default='BG')    
    
    class Meta:
        ordering = ['start','title']
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("cal.views.event",args=[self.slug])
    
    def get_event_url(self):
        return reverse("cal.views.event",args=[self.slug])
    
    def get_gantt_url(self):
        return reverse("cal.views.gantt",args=[self.slug])
    
    def focus_verbose(self):
        return dict(Event.FOCUS_CHOICES)[self.focus]
    
    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)
        date = self.start
        if self.slug is None or self.slug == "":
            self.slug = '%s-%i%i%i%i' % (
                slugify(self.title), date.year, date.month, date.day, self.id
            )
        if len(self.tasks.all())==0:
            self.tasks.create(
                name = "Attend "+self.title,
                description = self.description,
                code = "MEET",
                level = 1,
                order = 999,
                status = "STATUS_SUSPENDED",
                start = self.start,
                end = self.end,
                endIsMilestone = True
            )
        super(Event, self).save(*args, **kwargs)
        
class Role(models.Model):
    name = models.CharField(max_length=255,unique=True)
    
    def __str__(self):
        return self.name

class Assignee(models.Model):
    resource = models.ForeignKey(User)
    role = models.ForeignKey(Role,blank=True,null=True)
    effort = models.BigIntegerField(default=0)
    
    def __str__(self):
        return self.resource.get_full_name()+" as "+self.role.name

class Task(models.Model):
    name = models.CharField(max_length=255,blank=True,null=True)
    code = models.CharField(max_length=255,blank=True,null=True)
    level = models.IntegerField(blank=True,null=True)
    order = models.IntegerField(blank=True,null=True)
    STATUS_LEVELS = (
        ("STATUS_ACTIVE","STATUS_ACTIVE"),
        ("STATUS_DONE","STATUS_DONE"),
        ("STATUS_FAILED","STATUS_FAILED"),
        ("STATUS_SUSPENDED","STATUS_SUSPENDED"),
        ("STATUS_UNDEFINED","STATUS_UNDEFINED"),
    )
    status = models.CharField(max_length=255,choices=STATUS_LEVELS,default="STATUS_UNDEFINED")
    start = models.DateField(auto_now=False, auto_now_add=False)
    duration = models.IntegerField(blank=True,null=True)
    end = models.DateField(auto_now=False, auto_now_add=False)
    startIsMilestone = models.BooleanField(default=False)
    endIsMilestone = models.BooleanField(default=False)
    assignee = models.ManyToManyField(Assignee, related_name="tasks", related_query_name="task",blank=True)
    depends = models.CharField(max_length=255,blank=True,null=True)
    description = models.TextField(null=True,blank=True)
    progress = models.IntegerField(default=0)
    event = models.ForeignKey(Event, related_name="tasks", related_query_name="task",blank=True)
    hasChild = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['start','name']
    
    def __str__(self):
        return self.name
    