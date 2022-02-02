from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('login',Login),
    path('manager-dashboard', ManagerDashboard),
    path('hr-dashboard', HRDashboard),
    path('job-requisition', job_requisition),
    path("job-requisition-edit/<int:id>", jobRequisitionEditView),
    path("job-requisition-update", jobRequisitionEditUpdate),
    path("job-requisition-table-hr", jobRequisitionOpen),
    path("job-requisition-table/<str:type>", jobRequisitionSelf),
    path("job-requisition-all/<str:type>",jobRequisitionAll),
    path("settings", change_password)
]
