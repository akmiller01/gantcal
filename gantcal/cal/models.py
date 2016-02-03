from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    start = models.DateTimeField(auto_now=False, auto_now_add=False)
    end = models.DateTimeField(auto_now=False, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, auto_now_add=False)
    creator = models.ForeignKey(User, null=True, blank=True,editable=False)

    class Meta:
        ordering = ['start','title']
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("cal.views.month",args=[self.start.year,"%02d" % self.start.month])