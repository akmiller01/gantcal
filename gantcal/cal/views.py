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
from cal.models import Process
from django.contrib.auth.models import User
from cal.utils import uni
from django.contrib.auth.decorators import login_required
from django.http import *
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import CreateView
from itertools import chain

def login_user(request):
    logout(request)
    nextURL = request.GET.get('next')
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        nextURL = request.POST.get('next')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if nextURL is not None:
                  return HttpResponseRedirect(nextURL)
                else:
                  return HttpResponseRedirect('/')
    return render_to_response('cal/login.html',{'next':nextURL}, context_instance=RequestContext(request))

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
    start__gte=now, start__lte=now+timedelta(14)
  )
  events = Event.objects.order_by('start').filter(
    start__gte=now, start__lte=now+timedelta(14)
  )
  processes = Process.objects.order_by('start').filter(
    end__gte=now
  )
  return render_to_response('cal/dashboard.html', {"user":user,"userTasks":userTasks,"userEvents":userEvents,"events":events,"tasks":tasks,"processes":processes})

@login_required
def month(request):
  user = request.user
  now = datetime.now()
  year = request.GET.get('y')
  month = request.GET.get('m')
  if year is None or month is None:
    year = now.year
    month = now.month
  events = Event.objects.order_by('start').all()
  tasks = Task.objects.order_by('start').all()
  return render_to_response('cal/cal.html', {'events': events,'tasks': tasks,'year': year,'month':month,"user":user})

@login_required
def event(request,slug):
  user = request.user
  event = get_object_or_404(Event,slug=slug)
  return render_to_response('cal/event.html',{'event':event,"user":user})

@login_required
def gantt(request,slug):
  isProcess = False
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
  return render_to_response('cal/gantt.html',{'isProcess':isProcess,'event':metaEvent,'tasks':serializers.serialize('json',tasks),'assignees':json.dumps(assigneeDict),'roles':json.dumps(roleDict),'resources':json.dumps(resources),"user":authUser})

@login_required
def processGantt(request,slug):
  isProcess = True
  authUser = request.user
  process = get_object_or_404(Process,slug=slug)
  metaTasks = process.events.order_by('start').all()
  # for event in process.events.all():
  #   tasks = event.tasks.order_by('order')
  #   metaTasks.append(tasks)
  # metaTasks = [item for sublist in metaTasks for item in sublist]
  assignees = User.objects.all()
  assigneeDict = {"pk_"+str(assignee.id):{"id":"pk_"+str(assignee.id),"resourceId":"pk_"+str(assignee.id),"roleId":"pk_1","effort":0} for assignee in assignees}
  roleDict = [{"name":"Attendee","id":"pk_1"}]
  users = User.objects.all()
  resources = [{"name":uni(user.first_name+" "+user.last_name),"id":"pk_"+str(user.id)} for user in users]
  return render_to_response('cal/gantt.html',{'isProcess':isProcess,'event':process,'tasks':serializers.serialize('json',metaTasks),'assignees':json.dumps(assigneeDict),'roles':json.dumps(roleDict),'resources':json.dumps(resources),"user":authUser})


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
      task['id'] = taskInstance.pk
      currentAssigneePKs = []
      for assignee in task['assigs']:
        resourcePK = int(assignee['resourceId'][3:])
        rolePK = int(assignee['roleId'][3:])
        resource = User.objects.get(pk=resourcePK)
        role = Role.objects.get(pk=rolePK)
        effort=assignee['effort']
        #New assignees
        if "tmp" in str(assignee['id']):
          assigneeInstance = Assignee(
            resource=resource,
            role=role,
            effort=effort
          )
        else:
          #Update existing assignee
          assigneePK = int(assignee['id'][3:])
          assigneeInstance = Assignee.objects.get(pk=assigneePK)
          assigneeInstance.resource=resource
          assigneeInstance.role=role
          assigneeInstance.effort=effort
        assigneeInstance.save()
        assignee['id'] = assigneeInstance.pk
        currentAssigneePKs.append(assigneeInstance.pk)
        taskInstance.assignee.add(assigneeInstance)
      #Remove stale assignees
      for assigneeInstance in taskInstance.assignee.all():
        if assigneeInstance.pk not in currentAssigneePKs:
          taskInstance.assignee.remove(assigneeInstance)
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
      currentAssigneePKs = []
      for assignee in task['assigs']:
        resourcePK = int(assignee['resourceId'][3:])
        rolePK = int(assignee['roleId'][3:])
        resource = User.objects.get(pk=resourcePK)
        role = Role.objects.get(pk=rolePK)
        effort=assignee['effort']
        #New assignees
        if "tmp" in str(assignee['id']):
          assigneeInstance = Assignee(
            resource=resource,
            role=role,
            effort=effort
          )
        else:
          #Update existing assignee
          assigneePK = int(assignee['id'][3:])
          assigneeInstance = Assignee.objects.get(pk=assigneePK)
          assigneeInstance.resource=resource
          assigneeInstance.role=role
          assigneeInstance.effort=effort
        assigneeInstance.save()
        assignee['id'] = assigneeInstance.pk
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