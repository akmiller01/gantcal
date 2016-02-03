from django.shortcuts import render
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from cal.utils import EventCalendar
from cal.models import Event

def month(request, year, month):
  year = int(year)
  month = int(month)
  events = Event.objects.order_by('start').filter(
    start__year=year, start__month=month
  )
  cal = EventCalendar(events).formatmonth(year, month)
  return render_to_response('cal/index.html', {'calendar': mark_safe(cal),})
