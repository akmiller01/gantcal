from django.contrib import admin
from cal.models import Event
from cal.models import Theme
from cal.models import Process
from cal.models import Task
from cal.models import Tag
from cal.models import Role
from cal.models import Assignee

class RoleAdmin(admin.ModelAdmin):
    #fields display on change list
    list_display = ['name']
    #enable the save buttons on top of change form
    save_on_top = True

class AssigneeAdmin(admin.ModelAdmin):
    #fields display on change list
    list_display = ['resource','role']
    #enable the save buttons on top of change form
    save_on_top = True

class ThemeAdmin(admin.ModelAdmin):
    #fields display on change list
    list_display = ['title','description']
    #enable the save buttons on top of change form
    save_on_top = True

class ProcessAdmin(admin.ModelAdmin):
     #fields display on change list
    list_display = ['title','start','end']
    #fields to filter the change list with
    list_filter = ['theme','start']
    #fields to search in change list
    search_fields = ['title','description']
    #enable the date drill down on change list
    date_hierarchy = 'start'
    #enable the save buttons on top of change form
    save_on_top = True

class TaskAdmin(admin.ModelAdmin):
    #fields display on change list
    list_display = ['name','start','end','event']
    #fields to filter the change list with
    list_filter = ['event']
    #fields to search in change list
    search_fields = ['name','description']
    #enable the date drill down on change list
    date_hierarchy = 'start'
    #enable the save buttons on top of change form
    save_on_top = True

class TagAdmin(admin.ModelAdmin):
    #fields display on change list
    list_display = ['title']
    #enable the save buttons on top of change form
    save_on_top = True

class EventAdmin(admin.ModelAdmin):
    #fields display on change list
    list_display = ['title','description','start','end']
    #fields to filter the change list with
    list_filter = ['created']
    #fields to search in change list
    search_fields = ['title','description','content']
    #enable the date drill down on change list
    date_hierarchy = 'start'
    #enable the save buttons on top of change form
    save_on_top = True
    
    def save_model(self, request, obj, form, change):
        if getattr(obj, 'holder', None) is None:
            obj.holder = request.user
        obj.save()
        
admin.site.register(Role,RoleAdmin)
admin.site.register(Assignee,AssigneeAdmin)
admin.site.register(Theme,ThemeAdmin)
admin.site.register(Task,TaskAdmin)
admin.site.register(Process,ProcessAdmin)
admin.site.register(Tag,TagAdmin)
admin.site.register(Event,EventAdmin)
