from django.contrib import admin
from cal.models import Event

class EventAdmin(admin.ModelAdmin):
    #fields display on change list
    list_display = ['title','description','start','end']
    #fields to filter the change list with
    list_filter = ['created','creator']
    #fields to search in change list
    search_fields = ['title','description','content']
    #enable the date drill down on change list
    date_hierarchy = 'start'
    #enable the save buttons on top of change form
    save_on_top = True
    #prepopulate the slug from the title
    prepopulated_fields = {"slug":("title","start")}
    
    def save_model(self, request, obj, form, change):
        if getattr(obj, 'creator', None) is None:
            obj.author = request.user
        obj.save()
        
admin.site.register(Event,EventAdmin)
