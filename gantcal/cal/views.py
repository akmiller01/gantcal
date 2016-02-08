from datetime import datetime
from json import dumps
from django.core import serializers
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from cal.models import Event

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
  event = get_object_or_404(Event,slug=slug)
  return render_to_response('cal/event.html',{'event':event})