from datetime import datetime
from json import dumps
from django.core import serializers
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render_to_response, redirect
from django.utils.safestring import mark_safe
from cal.models import Event
from cal.models import Task
from cal.models import Assignee
from cal.models import Role
from django.contrib.auth.models import User
from cal.utils import uni
from django.contrib.auth.decorators import login_required
from django.http import *
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout

def login_user(request):
    nextURL = request.GET.get('next')
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if nextURL is not None:
                  return HttpResponseRedirect(nextURL)
                else:
                  return HttpResponseRedirect('/')
    return render_to_response('cal/login.html', context_instance=RequestContext(request))

@login_required
def dashboard(request):
  user = request.user
  tasks = Task.objects.order_by('start').filter(
    assignee__resource=user
  )
  return render_to_response('cal/dashboard.html', {"user":user,"tasks":tasks})

@login_required
def month(request):
  user = request.user
  now = datetime.now()
  year = request.GET.get('y')
  month = request.GET.get('m')
  if year is None or month is None:
    year = now.year
    month = now.month
  events = Event.objects.order_by('start').filter(
    start__year=year, start__month=month
  )
  return render_to_response('cal/cal.html', {'events': serializers.serialize('json',events),'year': year,'month':month,"user":user})

@login_required
def event(request,slug):
  user = request.user
  metaEvent = get_object_or_404(Event,slug=slug)
  tasks = Task.objects.filter(
    event=metaEvent
  )
  assignees = Assignee.objects.all()
  assigneeDict = {"pk_"+str(assignee.id):{"id":"pk_"+str(assignee.id),"resourceId":"pk_"+str(assignee.resource.id),"roleId":"pk_"+str(assignee.role.id),"effort":assignee.effort} for assignee in assignees}
  roles = Role.objects.all()
  roleDict = [{"name":uni(role.name),"id":"pk_"+str(role.id)} for role in roles]
  users = User.objects.all()
  resources = [{"name":uni(user.first_name+" "+user.last_name),"id":"pk_"+str(user.id)} for user in users]
  return render_to_response('cal/event.html',{'event':metaEvent,'tasks':serializers.serialize('json',tasks),'assignees':dumps(assigneeDict),'roles':dumps(roleDict),'resources':dumps(resources),"user":user})