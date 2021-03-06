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
    
    def __unicode__(self):
        return u'%s' % self.title
    
    def get_absolute_url(self):
        return reverse("cal.views.theme_gantt",args=[self.slug])
    
    def save(self, *args, **kwargs):
        super(Theme, self).save(*args, **kwargs)
        if self.slug is None or self.slug == "":
            self.slug = '%s-%i' % (
                slugify(self.title), self.id
            )
        super(Theme, self).save(*args, **kwargs)

class CrossCuttingArea(models.Model):
    title = models.CharField(max_length=255,unique=True)
    slug = models.SlugField(max_length=255,unique=True,editable=False)
    description = models.TextField(null=True,blank=True)
    start = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    end = models.DateField(auto_now=False, auto_now_add=False)
    theme = models.ManyToManyField(Theme, related_name="cross_cutting_areas", related_query_name="cross_cutting_area",blank=True)

    class Meta:
        ordering = ['start','title']
        verbose_name_plural = "cross cutting areas"
    
    def __unicode__(self):
        return u'%s' % self.title
    
    def get_absolute_url(self):
        return reverse("cal.views.cross_cutting_gantt",args=[self.slug])
    
    def save(self, *args, **kwargs):
        super(CrossCuttingArea, self).save(*args, **kwargs)
        if self.slug is None or self.slug == "":
            self.slug = '%s-%i' % (
                slugify(self.title), self.id
            )
        super(CrossCuttingArea, self).save(*args, **kwargs)
    
class Tag(models.Model):
    title = models.CharField(max_length=255,unique=True)
    slug = models.SlugField(max_length=255,unique=True,editable=False)
    
    class Meta:
        ordering = ['title']
    
    def __unicode__(self):
        return u'%s' % self.title
    
    def save(self, *args, **kwargs):
        super(Tag, self).save(*args, **kwargs)
        if self.slug is None or self.slug == "":
            self.slug = '%s-%i' % (
                slugify(self.title), self.id
            )
        super(Tag, self).save(*args, **kwargs)

class Attachment(models.Model):
    creator = models.ForeignKey(User, editable=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    modifier = models.ForeignKey(User,editable=False,related_name="modified_attachment")
    modified = models.DateTimeField(auto_now=True)
    upload = models.FileField(upload_to='%Y/%m/%d/', max_length=500)
    
    class Meta:
        ordering = ['modified']
    
    def __unicode__(self):
        return u'%s' % str(self.upload)

class Funder(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True,blank=True)
    
    def __unicode__(self):
        return u'%s' % self.name

class Event(models.Model):
    title = models.CharField(max_length=2000)
    description = models.TextField(default="")
    objectives = models.TextField(null=True,blank=True)
    notes = models.TextField(null=True,blank=True)
    event_URL = models.URLField(max_length=2000,null=True,blank=True)
    attendee = models.ManyToManyField(User,related_name="events",related_query_name="event",blank=True)
    lead = models.ForeignKey(User,null=True,blank=True)
    location = models.CharField(max_length=255,null=True,blank=True)
    slug = models.SlugField(unique=True,max_length=255, null=True, blank=True,editable=False)
    start = models.DateField(auto_now=False, auto_now_add=False)
    date_confirmed = models.BooleanField(default=True)
    end = models.DateField(auto_now=False, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, auto_now_add=False)
    tag = models.ManyToManyField(Tag, related_name="events", related_query_name="event",blank=True)
    theme = models.ManyToManyField(Theme, related_name="events", related_query_name="event",blank=True)
    cross_cutting_area = models.ManyToManyField(CrossCuttingArea, related_name="events", related_query_name="event",blank=True)
    funders = models.ManyToManyField(Funder,blank=True)
    estimated_cost = models.IntegerField(blank=True,null=True)
    PRIORITY_CHOICES = zip( range(1,4), range(1,4) )
    priority = models.IntegerField(choices=PRIORITY_CHOICES,blank=True,null=True)
    FOCUS_CHOICES = (
        ('AT','Attending'),
        # ('PR','Presenting'),
        # ('SE','Organising side event'),
        # ('LR','Launching report'),
        ('MO','Monitoring'),
        # ('MF','Monitoring and follow-up'),
        ('RE','Remotely engage'),
    )
    focus = models.CharField(max_length=2,choices=FOCUS_CHOICES,default='MO')
    COLOR_CHOICES = (
        ('#BA0C2F','Leadership team meetings'),
        ('#EA7600','Tony and Judith meeting'),
        ('#93328E','Global days'),
        ('#1B365D','External event or meeting'),
        ('#0095CB','Policy process milestones'),
    )
    attachments = models.ManyToManyField(Attachment,related_name="events",related_query_name="event",blank=True)
    type = models.CharField(max_length=7,choices=COLOR_CHOICES,default="#1B365D")
    objectives_approved = models.BooleanField(default=False)
    attendees_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['start','title']
    
    def __unicode__(self):
        return u'%s' % self.title

    def get_absolute_url(self):
        return reverse("cal.views.event",args=[self.slug])
    
    def get_event_url(self):
        return reverse("cal.views.event",args=[self.slug])
    
    def get_gantt_url(self):
        return reverse("cal.views.gantt",args=[self.slug])
    
    def focus_verbose(self):
        return dict(Event.FOCUS_CHOICES)[self.focus]
    
    def type_verbose(self):
        return dict(Event.COLOR_CHOICES)[self.type]
    
    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)
        date = self.start
        if self.title:
            self.title = self.title.replace('"',"'")
        if self.objectives:
            self.objectives = self.objectives.replace('"',"'")
        if self.description:
            self.description = self.description.replace('"',"'")
        if self.location:
            self.location = self.location.replace('"',"'")
        if self.slug is None or self.slug == "":
            self.slug = '%s-%i%i%i%i' % (
                slugify(self.title), date.year, date.month, date.day, self.id
            )
        # Stop automatic creation of tasks
        # if len(self.tasks.all())==0:
        #     self.tasks.create(
        #         name = self.title,
        #         description = self.description,
        #         code = "MEET",
        #         level = 1,
        #         order = 999,
        #         status = "STATUS_SUSPENDED",
        #         start = self.start,
        #         end = self.end,
        #         endIsMilestone = True
        #     )
        #Automatic attending labeling
        # if len(self.attendee.all())>0:
        #     self.focus = 'AT'
        super(Event, self).save(*args, **kwargs)
        
class Role(models.Model):
    name = models.CharField(max_length=255,unique=True)
    
    def __unicode__(self):
        return u'%s' % self.name

class Assignee(models.Model):
    resource = models.ForeignKey(User)
    role = models.ForeignKey(Role,blank=True,null=True)
    effort = models.BigIntegerField(default=0)
    
    def __unicode__(self):
        return u'%s' % self.resource.get_full_name()+" as "+self.role.name

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
    
    def __unicode__(self):
        return u'%s' % self.name
    
    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.replace('"',"'")
        if self.code:
            self.code = self.code.replace('"',"'")
        if self.description:
            self.description = self.description.replace('"',"'")
        if self.depends:
            self.depends = self.depends.replace('"',"'")
        super(Task, self).save(*args, **kwargs)
    