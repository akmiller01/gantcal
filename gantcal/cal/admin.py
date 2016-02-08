from django.contrib import admin
from cal.models import Event
from cal.models import Theme
from cal.models import Process
from cal.models import Activity
from cal.models import Tag

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

class ActivityAdmin(admin.ModelAdmin):
    #fields display on change list
    list_display = ['title','start','end','event']
    #fields to filter the change list with
    list_filter = ['event']
    #fields to search in change list
    search_fields = ['title','description']
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
    list_filter = ['created','holder']
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
        
admin.site.register(Theme,ThemeAdmin)
admin.site.register(Activity,ActivityAdmin)
admin.site.register(Process,ProcessAdmin)
admin.site.register(Tag,TagAdmin)
admin.site.register(Event,EventAdmin)
