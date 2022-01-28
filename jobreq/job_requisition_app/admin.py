from django.contrib import admin
from .models import *
# Register your models here

class ProfileSearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_id')
    list_display = ('emp_name','emp_id', 'emp_desi','emp_process',"emp_rm1_id","emp_rm2_id","emp_rm3_id")
class JobSearch(admin.ModelAdmin):
    search_fields = ('req_raised_by','created_by_id')
    list_display = ("id",'req_raised_by','created_by_id', 'requisition_date','hc_req',"status")

class TicketSearch(admin.ModelAdmin):
    search_fields = ("job_requisition_id", 'created_by', 'created_by_id')
    list_display = ("job_requisition_id", 'created_by', 'created_by_id', 'created_date')

admin.site.register(Profile, ProfileSearch)
admin.site.register(JobRequisition, JobSearch)
admin.site.register(Tickets, TicketSearch)