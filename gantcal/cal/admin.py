from datetime import timedelta
from datetime import datetime
from django.contrib import admin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Count
from cal.models import Event
from cal.models import Theme
from cal.models import CrossCuttingArea
from cal.models import Task
from cal.models import Tag
from cal.models import Role
from cal.models import Assignee
from cal.models import Attachment
from cal.models import Funder
import cgi

class ViewAdmin(admin.ModelAdmin):

    """
    Custom made change_form template just for viewing purposes
    You need to copy this from /django/contrib/admin/templates/admin/change_form.html
    And then put that in your template folder that is specified in the 
    settings.TEMPLATE_DIR
    """
    change_form_template = 'view_form.html'

    # Remove the delete Admin Action for this Model
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        #Return nothing to make sure user can't update any data
        pass

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

class CrossCuttingAreaAdmin(admin.ModelAdmin):
     #fields display on change list
    list_display = ['title','start','end']
    #fields to filter the change list with
    list_filter = ['start']
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
    
class FunderAdmin(admin.ModelAdmin):
    #fields display on change list
    list_display = ['name']
    #enable the save buttons on top of change form
    save_on_top = True

class AttachmentInline(admin.TabularInline):
    model = Attachment.events.through

class AttachmentAdmin(admin.ModelAdmin):
    #fields display on change list
    list_display = ['upload','modifier','modified','events']
    list_filter =['modified','creator','created']
    #enable the save buttons on top of change form
    save_on_top = True
    
    def events(self, obj):
        return "; ".join([event.title for event in obj.events.all()])
    
    def save_model(self, request, obj, form, change):
        user = request.user
        if not obj.pk:
            obj.creator = user
        obj.modifier = user
        return super(AttachmentAdmin, self).save_model(request, obj, form, change)
        

def approve_objectives(modeladmin, request, queryset):
    if request.user.has_perm('cal.add_event'):
        queryset.update(objectives_approved=True)
    else:
        messages.set_level(request, messages.ERROR)
        messages.error(request, 'You do not have permission to edit events')
        pass
approve_objectives.short_description = "Approve selected event objectives"

def unapprove_objectives(modeladmin, request, queryset):
    if request.user.has_perm('cal.add_event'):
        queryset.update(objectives_approved=False)
    else:
        messages.set_level(request, messages.ERROR)
        messages.error(request, 'You do not have permission to edit events')
        pass
unapprove_objectives.short_description = "Un-approve selected event objectives"

def approve_attendees(modeladmin, request, queryset):
    if request.user.has_perm('cal.add_event'):
        queryset.update(attendees_approved=True)
    else:
        messages.set_level(request, messages.ERROR)
        messages.error(request, 'You do not have permission to edit events')
        pass
approve_attendees.short_description = "Approve selected event attendees"

def unapprove_attendees(modeladmin, request, queryset):
    if request.user.has_perm('cal.add_event'):
        queryset.update(attendees_approved=False)
    else:
        messages.set_level(request, messages.ERROR)
        messages.error(request, 'You do not have permission to edit events')
        pass
unapprove_attendees.short_description = "Un-approve selected event attendees"

class EventTimeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = ('date')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            (None, ('All future events')),
            ('past', ('All past events')),
            ('all', ('All events')),
            ('weeks', ('Next 2 weeks')),
            ('month', ('Next month')),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }
    
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        now = datetime.now()
        if self.value() == None:
            return queryset.filter(start__gte=now)
        if self.value() == 'past':
            return queryset.filter(start__lte=now)
        if self.value() == 'all':
            return queryset
        if self.value() == 'weeks':
            return queryset.filter(start__gte=now, start__lte=now+timedelta(14))
        if self.value() == 'month':
            return queryset.filter(start__gte=now, start__lte=now+timedelta(31))

class EventAdmin(admin.ModelAdmin):
    
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("attachments", )
        form = super(EventAdmin, self).get_form(request, obj, **kwargs)
        return form
    
    #fields display on change list
    list_display = ['event_summary_title','confirmed_date','confirmed_date_end','location','priority','focus','objectives','short_objectives_approved','attendees','short_attendees_approved','edit']
    #fields to filter the change list with
    list_filter = [EventTimeFilter,'modified','priority','focus','start','tag','cross_cutting_area','theme','attendee','location']
    #fields to search in change list
    inlines = [AttachmentInline,]
    filter_horizontal = ('attendee','tag','theme','cross_cutting_area','funders')
    search_fields = ['title','description']
    #enable the date drill down on change list
    date_hierarchy = 'start'
    prepopulated_fields = {"end":("start",)}
    #enable the save buttons on top of change form
    save_on_top = True
    actions = [approve_objectives,approve_attendees,unapprove_objectives,unapprove_attendees]
    
    def edit(self,obj):
        return '<a href="%s">%s</a>' % (reverse("admin:cal_event_change", args=[obj.id]), "edit")
    edit.allow_tags = True
    
    def confirmed_date(self, obj):
        return '<span style="color:%s">%s</span>' % ("black" if obj.date_confirmed else "red", obj.start)
    confirmed_date.allow_tags = True
    confirmed_date.short_description = 'Start'
    confirmed_date.admin_order_field = 'start'
    
    def confirmed_date_end(self, obj):
        return '<span style="color:%s">%s</span>' % ("black" if obj.date_confirmed else "red", obj.end)
    confirmed_date.allow_tags = True
    confirmed_date.short_description = 'End'
    confirmed_date.admin_order_field = 'end'
    
    def short_objectives_approved(self,obj):
        return obj.objectives_approved
    short_objectives_approved.short_description = "Approved"
    short_objectives_approved.boolean = True
    short_objectives_approved.admin_order_field = 'objectives_approved'
    
    def short_attendees_approved(self,obj):
        return obj.attendees_approved
    short_attendees_approved.short_description = "Approved"
    short_attendees_approved.boolean = True
    short_attendees_approved.admin_order_field = 'attendees_approved'
    
    def event_summary_title(self, obj):
        return '<a href="%s">%s</a>' % (obj.get_event_url(), cgi.escape(obj.title))
    event_summary_title.allow_tags = True
    event_summary_title.short_description = 'Title'
    event_summary_title.admin_order_field = 'title'
    
    def attendees(self, obj):
        return "; ".join([p.get_full_name() for p in obj.attendee.all()])
    
    def save_model(self, request, obj, form, change):
        if not request.user.has_perm('cal.add_event'):
            messages.set_level(request, messages.ERROR)
            messages.error(request, 'You do not have permission to edit events')
            pass
        else:
            return super(EventAdmin, self).save_model(request, obj, form, change)
        
admin.site.register(Role,RoleAdmin)
admin.site.register(Assignee,AssigneeAdmin)
admin.site.register(Theme,ThemeAdmin)
admin.site.register(Task,TaskAdmin)
admin.site.register(CrossCuttingArea,CrossCuttingAreaAdmin)
admin.site.register(Tag,TagAdmin)
admin.site.register(Attachment,AttachmentAdmin)
admin.site.register(Event,EventAdmin)
admin.site.register(Funder,FunderAdmin)
