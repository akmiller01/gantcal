"""gantcal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from cal import views
from django.contrib.auth.views import login, logout, password_change
from axes.decorators import watch_login

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^admin/', admin.site.urls),
    url(r'^login', watch_login(views.login_user), name='login'),
    url(r'^calendar/$', views.month, name='month'),
    url(r'^ical/events.ics$', views.ical_event, name='icalEvent'),
    url(r'^ical/tasks.ics$', views.ical_task, name='icalTask'),
    url(r'^(?P<slug>[\w\-]+)/$', views.event,name='event'),
    url(r'^g/(?P<slug>[\w\-]+)/$', views.gantt,name='gantt'),
    url(r'^g/(?P<slug>[\w\-]+)/ganttAjax$', views.ganttAjax,name='ganttAjax'),
    url(r'^c/(?P<slug>[\w\-]+)/$', views.cross_cutting_gantt,name='cross_cutting_gantt'),
    url(r'^t/(?P<slug>[\w\-]+)/$', views.theme_gantt,name='theme_gantt'),
    url(r'^g/([\w\-]+)/res/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^c/([\w\-]+)/res/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^t/([\w\-]+)/res/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
]
