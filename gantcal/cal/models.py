from __future__ import unicode_literals

from django.db import models
from django.db.models.fields import Field
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from datetime import datetime
from django.utils.text import slugify

class MyBooleanField(models.BooleanField):

    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "MyBooleanField"

    def db_type(self, connection):
        return "text"

    def to_python(self, value):
        if value in (True, False): return value
        if value in ('t', 'True', 'true', '1', '\x01'): return True  
        if value in ('f', 'False', 'false', '0', '\x00'): return False

    def get_db_prep_value(self, value, connection,prepared=False):
        value = super(MyBooleanField, self).get_db_prep_value(value, connection, prepared)
        return 'true' if value else 'false'

class BooleanField(Field):
    empty_strings_allowed = False
    default_error_messages = {
        'invalid': ("'%(value)s' value must be either True or False."),
    }
    description = ("Boolean (Either True or False)")

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        super(BooleanField, self).__init__(*args, **kwargs)

    def check(self, **kwargs):
        errors = super(BooleanField, self).check(**kwargs)
        errors.extend(self._check_null(**kwargs))
        return errors

    def _check_null(self, **kwargs):
        if getattr(self, 'null', False):
            return [
                checks.Error(
                    'BooleanFields do not accept null values.',
                    hint='Use a NullBooleanField instead.',
                    obj=self,
                    id='fields.E110',
                )
            ]
        else:
            return []

    def deconstruct(self):
        name, path, args, kwargs = super(BooleanField, self).deconstruct()
        del kwargs['blank']
        return name, path, args, kwargs

    def get_internal_type(self):
        return "BooleanField"

    def to_python(self, value):
        if value in (True, False):
            # if value is 1 or 0 than it's equal to True or False, but we want
            # to return a true bool for semantic reasons.
            return bool(value)
        if value in ('t', 'True', 'true', '1'):
            return True
        if value in ('f', 'False', 'false', '0'):
            return False
        raise exceptions.ValidationError(
            self.error_messages['invalid'],
            code='invalid',
            params={'value': value},
        )

    def get_prep_lookup(self, lookup_type, value):
        # Special-case handling for filters coming from a Web request (e.g. the
        # admin interface). Only works for scalar values (not lists). If you're
        # passing in a list, you might as well make things the right type when
        # constructing the list.
        if value in ('1', '0'):
            value = bool(int(value))
        return super(BooleanField, self).get_prep_lookup(lookup_type, value)

    def get_prep_value(self, value):
        value = super(BooleanField, self).get_prep_value(value)
        if value is None:
            return None
        return bool(value)

    def formfield(self, **kwargs):
        # Unlike most fields, BooleanField figures out include_blank from
        # self.null instead of self.blank.
        if self.choices:
            include_blank = not (self.has_default() or 'initial' in kwargs)
            defaults = {'choices': self.get_choices(include_blank=include_blank)}
        else:
            defaults = {'form_class': forms.BooleanField}
        defaults.update(kwargs)
        return super(BooleanField, self).formfield(**defaults)
    
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
    end = models.DateField(auto_now=False, auto_now_add=False)
    theme = models.ManyToManyField(Theme, related_name="processes", related_query_name="process",blank=True)
    
    class Meta:
        ordering = ['start','title']
        verbose_name_plural = "processes"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("cal.views.processGantt",args=[self.slug])
    
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
    objectives = models.TextField(null=True,blank=True)
    attendee = models.ManyToManyField(User,related_name="events",related_query_name="event",blank=True)
    location = models.CharField(max_length=255,null=True,blank=True)
    slug = models.SlugField(unique=True,max_length=255, null=True, blank=True,editable=False)
    start = models.DateField(auto_now=False, auto_now_add=False)
    date_confirmed = models.BooleanField(default=True)
    end = models.DateField(auto_now=False, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, auto_now_add=False)
    tag = models.ManyToManyField(Tag, related_name="events", related_query_name="event",blank=True)
    process = models.ManyToManyField(Process, related_name="events", related_query_name="event",blank=True)
    PRIORITY_CHOICES = zip( range(1,4), range(1,4) )
    priority = models.IntegerField(choices=PRIORITY_CHOICES,blank=True,null=True)
    estimated_cost = models.IntegerField(blank=True,null=True)
    FOCUS_CHOICES = (
        ('AT','Attending'),
        ('PR','Presenting'),
        ('SE','Organising side event'),
        ('LR','Launching report'),
        ('MO','Monitoring'),
        ('MF','Monitoring and follow-up'),
        ('RE','Remotely engage'),
    )
    focus = models.CharField(max_length=2,choices=FOCUS_CHOICES,default='MO')
    objectives_approved = models.BooleanField(default=False)
    attendees_approved = models.BooleanField(default=False)
    
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
                name = self.title,
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
    