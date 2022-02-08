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
    path('job-requisition-manager-update',job_requisition_manager_edit), # For updating the requisition
    path("settings", change_password),
    path('dashboard',dashboardRedirects),
    path('edit-requisition', EditRequest),
    path('createuser',createUserandProfile),
    path('approval', approval),
]
