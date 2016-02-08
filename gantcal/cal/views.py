from datetime import datetime
from json import dumps
from django.core import serializers
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from cal.models import Event
from cal.models import Task
from cal.models import Assignee
from cal.models import Role
from django.contrib.auth.models import User
from cal.utils import uni

def month(request):
  now = datetime.now()
  year = request.GET.get('y')
  month = request.GET.get('m')
  if year is None or month is None:
    year = now.year
    month = now.month
  events = Event.objects.order_by('start').filter(
    start__year=year, start__month=month
  )
  return render_to_response('cal/index.html', {'events': serializers.serialize('json',events),'year': year,'month':month})

def event(request,slug):
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
  return render_to_response('cal/event.html',{'event':metaEvent,'tasks':serializers.serialize('json',tasks),'assignees':dumps(assigneeDict),'roles':dumps(roleDict),'resources':dumps(resources)})