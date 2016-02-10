from datetime import timedelta
from datetime import datetime
import json
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
  now = datetime.now()
  user = request.user
  userTasks = Task.objects.order_by('start').filter(
    assignee__resource=user
  )
  userEvents = Event.objects.order_by('start').filter(
    attendee=user
  )
  tasks = Task.objects.order_by('start').filter(
    start__gt=now, start__lt=now+timedelta(14)
  )
  events = Event.objects.order_by('start').filter(
    start__gt=now, start__lt=now+timedelta(14)
  )
  return render_to_response('cal/dashboard.html', {"user":user,"userTasks":userTasks,"userEvents":userEvents,"events":events,"tasks":tasks})

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
  tasks = Task.objects.order_by('start').filter(
    start__year=year, start__month=month
  )
  return render_to_response('cal/cal.html', {'events': events,'tasks': tasks,'year': year,'month':month,"user":user})

@login_required
def event(request,slug):
  user = request.user
  event = get_object_or_404(Event,slug=slug)
  return render_to_response('cal/event.html',{'event':event,"user":user})

@login_required
def gantt(request,slug):
  authUser = request.user
  metaEvent = get_object_or_404(Event,slug=slug)
  tasks = Task.objects.filter(
    event=metaEvent
  ).order_by('order')
  assignees = Assignee.objects.all()
  assigneeDict = {"pk_"+str(assignee.id):{"id":"pk_"+str(assignee.id),"resourceId":"pk_"+str(assignee.resource.id),"roleId":"pk_"+str(assignee.role.id),"effort":assignee.effort} for assignee in assignees}
  roles = Role.objects.all()
  roleDict = [{"name":uni(role.name),"id":"pk_"+str(role.id)} for role in roles]
  users = User.objects.all()
  resources = [{"name":uni(user.first_name+" "+user.last_name),"id":"pk_"+str(user.id)} for user in users]
  return render_to_response('cal/gantt.html',{'event':metaEvent,'tasks':serializers.serialize('json',tasks),'assignees':json.dumps(assigneeDict),'roles':json.dumps(roleDict),'resources':json.dumps(resources),"user":authUser})

def ganttAjax(request,slug):
  project = json.loads(request.POST['prj'])
  event = Event.objects.get(slug=slug)
  #Check to see if there are any new tasks
  newTasks = project['tasks']
  currentTaskPKs = []
  for (idx,task) in enumerate(newTasks):
    if "tmp" in str(task['id']):
      taskInstance = Task(
        name = task['name'],
        order = idx,
        code = task['code'],
        level = task['level'],
        status = task['status'],
        duration = task['duration'],
        startIsMilestone = task['startIsMilestone'],
        endIsMilestone = task['endIsMilestone'],
        depends = task['depends'],
        description = task['description'],
        progress = task['progress'],
        event = event,
        hasChild = task['hasChild'],
        start = datetime.fromtimestamp(task['start']/1000),
        end = datetime.fromtimestamp(task['end']/1000),
      )
      taskInstance.save()
      #Check to see if assignee exists, if not, make it
      for assignee in task['assigs']:
        resourcePK = int(assignee['resourceId'][3:])
        rolePK = int(assignee['roleId'][3:])
        resource = User.objects.get(pk=resourcePK)
        role = Role.objects.get(pk=rolePK)
        try:
          assigneeInstance = Assignee.objects.get(resource=resource,role=role)
        except Assignee.DoesNotExist:
          assigneeInstance = Assignee(
            resource=resource,
            role=role,
            effort=0
          )
          assigneeInstance.save()
        taskInstance.assignee.add(assigneeInstance)
      taskInstance.save()
      currentTaskPKs.append(taskInstance.pk)
    else:
      #Update the pre-existing task
      taskInstance = Task.objects.get(pk=task['id'])
      taskInstance.name = task['name']
      taskInstance.order = idx
      taskInstance.code = task['code']
      taskInstance.level = task['level']
      taskInstance.status = task['status']
      taskInstance.duration = task['duration']
      taskInstance.startIsMilestone = task['startIsMilestone']
      taskInstance.endIsMilestone = task['endIsMilestone']
      taskInstance.depends = task['depends']
      taskInstance.description = task['description']
      taskInstance.progress = task['progress']
      taskInstance.event = event
      taskInstance.hasChild = task['hasChild']
      taskInstance.start = datetime.fromtimestamp(task['start']/1000)
      taskInstance.end = datetime.fromtimestamp(task['end']/1000)
      #Check to see if assignee exists, if not, make it
      currentAssigneePKs = []
      for assignee in task['assigs']:
        resourcePK = int(assignee['resourceId'][3:])
        rolePK = int(assignee['roleId'][3:])
        resource = User.objects.get(pk=resourcePK)
        role = Role.objects.get(pk=rolePK)
        try:
          assigneeInstance = Assignee.objects.get(resource=resource,role=role)
          currentAssigneePKs.append(assigneeInstance.pk)
        except Assignee.DoesNotExist:
          assigneeInstance = Assignee(
            resource=resource,
            role=role,
            effort=0
          )
          assigneeInstance.save()
          currentAssigneePKs.append(assigneeInstance.pk)
        taskInstance.assignee.add(assigneeInstance)
      #Remove stale assignees
      for assigneeInstance in taskInstance.assignee.all():
        if assigneeInstance.pk not in currentAssigneePKs:
          taskInstance.assignee.remove(assigneeInstance)
      taskInstance.save()
      currentTaskPKs.append(taskInstance.pk)
  #Remove stale tasks
  tasks = Task.objects.filter(
    event=event
  )
  for taskInstance in tasks:
    if taskInstance.pk not in currentTaskPKs:
      taskInstance.delete()
  
  response_data = {}
  response_data['ok'] = True
  response_data['project'] = project
  response_data['result'] = 'success'
  response_data['message'] = ''
  response_data['errorMessages'] = []
  return JsonResponse(response_data)