import datetime
from datetime import date

import pytz
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import get_template
from django.template import context

from .models import *

# Create your views here.
number = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
# Designation List
hr_list = ['HR','HR Manager','Manager ER','HR Lead','Sr Recruiter','MIS Executive HR','Lead HRBP','Employee Relations Specialist','Payroll Specialist','Recruiter','HR Generalist']
am_mgr_list = ['Assistant Manager','Learning and Development Head','Quality Head','Operations Manager','Service Delivery Manager','Command Centre Head','Manager']
edit_list = ['Assistant Manager','Learning and Development Head','Quality Head','Operations Manager',
             'Service Delivery Manager','Command Centre Head','Manager','HR','HR Manager','Manager ER','HR Lead',
             'Sr Recruiter','MIS Executive HR','Lead HRBP','Employee Relations Specialist','Payroll Specialist',
             'Recruiter','HR Generalist']
mgr_list = ['Learning and Development Head','Quality Head','Operations Manager','Service Delivery Manager','Command Centre Head','Manager']

def index(request):
    logout(request)
    return render(request, "index.html")

def Login(request):
    if request.method == "POST":
        username = request.POST["user"]
        password = request.POST["pass"]
        user = authenticate(username=username, password=password)
        if user is not None:
            # user_login
            login(request, user)
            designation = request.user.profile.emp_desi

            if designation in am_mgr_list:
                return redirect("/erf/manager-dashboard")
            elif designation in hr_list:
                return redirect("/erf/hr-dashboard")
            else:
                messages.info(request, 'Not authorised to view this page !')
                return redirect("/erf/")

        else:
            messages.info(request, 'Invalid user !')
            return redirect("/erf/")
    else:
        pass

def dashboardRedirects(request):
    designation = request.user.profile.emp_desi
    if designation in am_mgr_list:
        return redirect("/erf/manager-dashboard")
    elif designation in hr_list:
        return redirect("/erf/hr-dashboard")
    else:
        messages.info(request, 'Not authorised to view this page !')
        return redirect("/erf/")


@login_required
def ManagerDashboard(request):
    designation = request.user.profile.emp_desi
    emp_id = request.user.profile.emp_id
    if designation in am_mgr_list:
        all = JobRequisition.objects.filter(created_by_id=emp_id).count()
        open = JobRequisition.objects.filter(created_by_id=emp_id,final_status=False).count()
        closed = JobRequisition.objects.filter(created_by_id=emp_id,final_status=True).count()
        dead_line = JobRequisition.objects.filter(created_by_id=emp_id,final_status=False)
        today = datetime.date.today()
        dead_line_count_list = []
        for i in dead_line:
            if i.dead_line < today:
                dead_line_count_list.append(i.id)
        dead_line_count = len(dead_line_count_list)
        approval = JobRequisition.objects.filter(created_by_manager_id=emp_id,initial_status=True,final_status=False).count()

        data = {"all":all,"open":open,"closed":closed,"dead_line":dead_line_count,"approval":approval,"manager":mgr_list}
        return render(request, "manager_dashboard.html",data)
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")

@login_required
def HRDashboard(request):
    designation = request.user.profile.emp_desi
    usr = request.user
    if designation in hr_list:
        manager = Profile.objects.all()
        all = JobRequisition.objects.all().count()
        open = JobRequisition.objects.filter(initial_status=False).count()
        closed = JobRequisition.objects.filter(final_status=True).count()
        added = JobRequisition.objects.filter(created_by_id=usr).count()
        waiting = JobRequisition.objects.filter(initial_status=True,final_status=False).count()
        data ={"all":all,"open":open,"closed":closed,"added":added,"manager":manager,"waiting":waiting}
        return render(request, "hr_dashboard.html",data)
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")

@login_required
def job_requisition(request):
    user = request.user.profile
    if request.method == "POST":
        requisition_date = datetime.datetime.now()
        today = str(datetime.date.today())
        hc_req = request.POST["hc_required"]
        req_raised_by = request.POST["req_rais_by"]
        created_by_id = request.user.profile.emp_id
        department = request.POST["department"]
        designation = request.POST["designation"]
        process_typ_one = request.POST["pro_type_1"]
        process_typ_two = request.POST["pro_type_2"]
        process_typ_three =request.POST["pro_type_3"]
        salary_rang_frm =request.POST["sal_from"]
        salary_rang_to = request.POST["sal_to"]
        qualification =request.POST["quali"]
        other_quali = request.POST["other_quali"]
        skills_set = request.POST["skills"]
        languages =request.POST.getlist("lang")
        shift_timing = request.POST["shift"]
        shift_timing_frm = request.POST["shift_from"]
        shift_timing_to = request.POST["shift_to"]
        type_of_working = request.POST["working_days"]
        working_from = request.POST.get("work_from")
        working_to = request.POST.get("work_to")
        week_no_days = request.POST.get("num_off")
        week_from = request.POST.get("off_from")
        week_to = request.POST.get("off_to")
        requisition_typ = request.POST["req_type"]
        replace_reason = request.POST["replace_reason"]
        manager_id = request.POST["manager"]
        manager = Profile.objects.get(emp_id=manager_id).emp_name
        dead_line = request.POST["dead_line"]
        campaign = request.POST["campaign"]
        unique_id = today+hc_req+created_by_id+department+designation+dead_line
        try:
            obj = JobRequisition.objects.get(unique_id=unique_id)
            if obj:
                messages.info(request, "Request added please wait!")
            if request.user.profile.emp_desi in am_mgr_list:
                return redirect("/erf/manager-dashboard")
            elif request.user.profile.emp_desi in hr_list:
                return redirect("/erf/hr-dashboard")
            else:
                messages.info(request, "Invalid Request. You have been logged out :)")
                return redirect("/erf/")

        except JobRequisition.DoesNotExist:
            e = JobRequisition()
            e.unique_id = unique_id
            e.campaign = campaign
            e.dead_line = dead_line
            e.type_of_working = type_of_working
            e.requisition_date = requisition_date
            e.hc_req = hc_req
            e.req_raised_by = req_raised_by
            e.created_by_manager = manager
            e.created_by_manager_id = manager_id
            e.department = department
            e.designation = designation
            e.process_type_one = process_typ_one
            e.process_type_two = process_typ_two
            e.process_type_three = process_typ_three
            e.salary_rang_frm = salary_rang_frm
            e.salary_rang_to = salary_rang_to
            e.qualification = qualification
            e.other_quali = other_quali
            e.skills_set = skills_set
            e.languages = languages
            e.shift_timing =shift_timing
            e.shift_timing_frm = shift_timing_frm
            e.shift_timing_to = shift_timing_to
            e.working_from = working_from
            e.working_to = working_to
            if week_no_days:
                e.week_no_days =week_no_days
            if week_from:
                e.week_from = week_from
            if week_to:
                e.week_to = week_to
            e.requisition_type = requisition_typ
            e.reason_for_replace = replace_reason
            e.created_by_id=created_by_id
            e.save()


            a = Tickets()
            a.job_requisition_id = e.id
            a.created_by = req_raised_by
            a.created_by_id = created_by_id
            a.created_date = requisition_date
            now_datetime = datetime.datetime.now().strftime('%b %d,%Y %H:%M:%S')
            a.edited_by = [now_datetime,req_raised_by,created_by_id,"Created"]
            a.save()
            messages.info(request, "Job Requisition Added Successfully !!")
            action = "Created"
            subject = action+" Job Requisition "+str(e.id)
            html_path = 'email.html'
            data = {'id': e.id,"created_date":requisition_date,"hc":hc_req,"department":department,"position":designation,
                    "deadline":dead_line,"campaign":campaign,"user":user.emp_name,"action":action,"status":"Pending"}
            email_template = get_template(html_path).render(data)
            to = [request.user.profile.emp_email,"aparna.ks@expertcallers.com"]
            email_msg = EmailMessage(subject,
                                     email_template, 'testm2063@gmail.com',
                                     to,
                                     reply_to=['qms@expertcallers.com'])
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)
            if request.user.profile.emp_desi in am_mgr_list:
                return redirect("/erf/manager-dashboard")
            elif request.user.profile.emp_desi in hr_list:
                return redirect("/erf/hr-dashboard")
            else:
                messages.info(request, "Invalid Request. You have been logged out :)")
                return redirect("/erf/")

    else:
        managers = Profile.objects.filter(emp_desi__in=mgr_list)
        today = date.today()
        campaigns = Campaigns.objects.all()
        data = {"today":today,"managers":managers,"campaigns":campaigns}
        return render(request, "job_requisition.html",data)

@login_required
def jobRequisitionOpen(request):
    designation = request.user.profile.emp_desi
    if designation in hr_list:
        job = JobRequisition.objects.filter(initial_status=False)
        data = {"job":job,"number":number,"type":"open",'desi':'hr',"editaccess":edit_list}
        return render(request, "job_requisition_table.html", data)
    else:
        messages.info(request,"Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def jobRequisitionSelf(request,type):
    user = request.user.profile.emp_id
    if type == "all":
        job = JobRequisition.objects.filter(created_by_id=user)
        data = {"job":job,"type":type,"number":number,"editaccess":edit_list}
        return render(request, "job_requisition_table.html", data)
    elif type == "open":
        job = JobRequisition.objects.filter(created_by_id=user,final_status=False)
        data = {"job": job,"type":type,"number":number,"editaccess":edit_list}
        return render(request, "job_requisition_table.html", data)
    elif type == "closed":
        job = JobRequisition.objects.filter(created_by_id=user,final_status=True)
        data = {"job": job,"type":type,"number":number,"editaccess":edit_list}
        return render(request, "job_requisition_table.html", data)
    elif type == "dead-line":
        today = datetime.date.today()
        job = JobRequisition.objects.filter(created_by_id=user,final_status=False)
        job_list = []
        for i in job:
            if i.dead_line < today:
                job_list.append(i)
        data = {"job": job_list,"type":type,"number":number,"editaccess":edit_list}
        return render(request, "job_requisition_table.html", data)
    elif type == "approval":
        job = JobRequisition.objects.filter(created_by_manager_id=user, initial_status=True,final_status=False)
        data = {"job": job,"type":type,"number":number,"editaccess":edit_list, "manager":mgr_list}
        return render(request, "job_requisition_table.html", data)
    elif type == "range":
        if request.method == "POST":
            status = request.POST["status"]
            start = request.POST["start_date"]
            end = request.POST["end_date"]
            if status == "all":
                job = JobRequisition.objects.filter(created_by_id=user,requisition_date__range=[start, end])
            elif status == "open":
                job = JobRequisition.objects.filter(created_by_id=user,final_status=False,requisition_date__range=[start, end])
            elif status == "closed":
                job = JobRequisition.objects.filter(created_by_id=user,final_status=True,requisition_date__range=[start, end])
            else:
                pass
            data = {"job":job,"type":type,"number":number,"editaccess":edit_list}
            return render(request, "job_requisition_table.html", data)
        else:
            messages.info(request, "Invalid Request. You have been logged out :)")
            return redirect("/erf/")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def jobRequisitionAll(request,type):
    if type == "all":
        job = JobRequisition.objects.all()
        data = {"job":job,"type":type,"number":number,"editaccess":edit_list}
        return render(request, "job_requisition_table.html", data)
    if type == "closed":
        job = JobRequisition.objects.filter(final_status=True)
        data = {"job":job,"type":type,"number":number,"editaccess":edit_list}
        return render(request, "job_requisition_table.html", data)
    elif type == "waiting":
        job = JobRequisition.objects.filter(initial_status=True,final_status=False)
        data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
        return render(request, "job_requisition_table.html", data)
    elif type == "range":
        if request.method == "POST":
            manager = request.POST["manager"]
            status = request.POST["status"]
            start = request.POST["start_date"]
            end = request.POST["end_date"]
            if manager == "all" and status == "all":
                job = JobRequisition.objects.filter(requisition_date__range=[start, end])
            elif manager == "all" and status == "open":
                job = JobRequisition.objects.filter(final_status=False, requisition_date__range=[start, end])
            elif manager == "all" and status == "closed":
                job = JobRequisition.objects.filter(final_status=True, requisition_date__range=[start, end])
            elif manager != "all" and status == "all":
                job = JobRequisition.objects.filter(created_by_id=manager,requisition_date__range=[start, end])
            elif manager != "all" and status == "open":
                job = JobRequisition.objects.filter(created_by_id=manager,final_status=False,requisition_date__range=[start, end])
            elif manager != "all" and status == "closed":
                job = JobRequisition.objects.filter(created_by_id=manager,final_status=True,requisition_date__range=[start, end])
            else:
                pass
            data = {"job":job,"type":type,"number":number,"editaccess":edit_list}
            return render(request, "job_requisition_table.html", data)
        else:
            messages.info(request, "Invalid Request. You have been logged out :)")
            return redirect("/erf/")
    elif type == "designation":
        if request.method == "POST":
            department = request.POST["department"]
            designation = request.POST.get("designation")
            start = request.POST.get("start_date")
            end = request.POST.get("end_date")
            if start:
                if designation:
                    job = JobRequisition.objects.filter(department=department, designation=designation,
                                                        requisition_date__range=[start, end])
                else:
                    job = JobRequisition.objects.filter(department=department, requisition_date__range=[start, end])
            else:
                if designation:
                    job = JobRequisition.objects.filter(department=department, designation=designation)
                else:
                    job = JobRequisition.objects.filter(department=department)

            data = {"job": job, "type": type, "number": number,"editaccess":edit_list}
            return render(request, "job_requisition_table.html", data)
        else:
            messages.info(request, "Invalid Request. You have been logged out :)")
            return redirect("/erf/")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def jobRequisitionEditView(request,id):
    designation = request.user.profile.emp_desi
    if designation in edit_list:
        try:
            job = JobRequisition.objects.get(id=id)
            today = date.today()
            campaigns = Campaigns.objects.all()
            employees = AllAgents.objects.all()
            data = {"today": today,"job":job,"number":number,"employees":employees,"campaigns":campaigns}
            return render(request, "job_requisition_edit.html", data)
        except JobRequisition.DoesNotExist:
            messages.info(request, "Invalid Request!!")
            if designation in hr_list:
                return redirect("/erf/hr-dashboard")
            elif designation in am_mgr_list:
                return redirect("/erf/manager-dashboard")
            else:
                messages.info(request, "Invalid Request!!. You have been logged out :)")
                return redirect("/erf/")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def EditRequest(request):
    designation = request.user.profile.emp_desi
    emp_id = request.user.profile.emp_id
    if request.method == "POST":
        id = request.POST["id"]
        by = request.POST["by"]
        start = JobRequisition.objects.get(id=id).requisition_date.timestamp()
        timee = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).timestamp() - start
        if timee <= 86400:
            if emp_id == by:
                job = JobRequisition.objects.get(id=id)
                managers = Profile.objects.filter(emp_desi__in=mgr_list)
                today = date.today()
                campaigns = Campaigns.objects.all()
                data = {"today": today, "managers": managers,"job": job,"campaigns":campaigns}
                return render(request, "edit_job_requisition.html", data)
            else:
                messages.info(request, "You are not authorize to edit this :)")
                if designation in hr_list:
                    return redirect("/erf/hr-dashboard")
                elif designation in am_mgr_list:
                    return redirect("/erf/manager-dashboard")
                else:
                    messages.info(request, "Invalid Request!! You have been logged out :)")
                    return redirect("/erf/")
        else:
            messages.info(request,"Can not Edit Now. Time limit has been exceeded :)")
            if designation in hr_list:
                return redirect("/erf/hr-dashboard")
            elif designation in am_mgr_list:
                return redirect("/erf/manager-dashboard")
            else:
                messages.info(request, "Invalid Request!!. You have been logged out :)")
                return redirect("/erf/")
    else:
        pass


@login_required
def job_requisition_manager_edit(request):
    user = request.user.profile
    if request.method == "POST":
        requisition_date = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        hc_req = request.POST["hc_required"]
        req_raised_by = request.POST["req_rais_by"]
        created_by_id = request.user.profile.emp_id
        department = request.POST["department"]
        designation = request.POST["designation"]
        process_typ_one = request.POST["pro_type_1"]
        process_typ_two = request.POST["pro_type_2"]
        process_typ_three =request.POST["pro_type_3"]
        salary_rang_frm =request.POST["sal_from"]
        salary_rang_to = request.POST["sal_to"]
        qualification =request.POST["quali"]
        other_quali = request.POST["other_quali"]
        skills_set = request.POST["skills"]
        languages =request.POST.getlist("lang")
        shift_timing = request.POST["shift"]
        shift_timing_frm = request.POST["shift_from"]
        shift_timing_to = request.POST["shift_to"]
        type_of_working = request.POST["working_days"]
        working_from = request.POST.get("work_from")
        working_to = request.POST.get("work_to")
        week_no_days = request.POST.get("num_off")
        week_from = request.POST.get("off_from")
        week_to = request.POST.get("off_to")
        requisition_typ = request.POST["req_type"]
        replace_reason = request.POST["replace_reason"]
        manager_id = request.POST["manager"]
        manager = Profile.objects.get(emp_id=manager_id).emp_name
        dead_line = request.POST["dead_line"]
        campaign = request.POST["campaign"]
        id = request.POST["id"]


        e = JobRequisition.objects.get(id=id)
        e.campaign = campaign
        e.dead_line = dead_line
        e.type_of_working = type_of_working
        e.requisition_date =requisition_date
        e.hc_req = hc_req
        e.req_raised_by = req_raised_by
        e.created_by_manager = manager
        e.created_by_manager_id = manager_id
        e.department = department
        e.designation = designation
        e.process_type_one = process_typ_one
        e.process_type_two = process_typ_two
        e.process_type_three = process_typ_three
        e.salary_rang_frm = salary_rang_frm
        e.salary_rang_to = salary_rang_to
        e.qualification = qualification
        e.other_quali = other_quali
        e.skills_set = skills_set
        e.languages = languages
        e.shift_timing =shift_timing
        e.shift_timing_frm = shift_timing_frm
        e.shift_timing_to = shift_timing_to
        e.working_from = working_from
        e.working_to = working_to
        if week_no_days:
            e.week_no_days =week_no_days
        if week_from:
            e.week_from = week_from
        if week_to:
            e.week_to = week_to
        e.requisition_type = requisition_typ
        e.reason_for_replace = replace_reason
        e.created_by_id=created_by_id
        e.save()

        a = Tickets.objects.get(job_requisition_id=id)
        a.job_requisition_id = e.id
        a.created_by = req_raised_by
        a.created_by_id = created_by_id
        a.created_date = requisition_date
        now_datetime = datetime.datetime.now().strftime('%b %d,%Y %H:%M:%S')
        edited_by = str([now_datetime, request.user.profile.emp_name, request.user.profile.emp_id, "Edited the request"])
        previous = a.edited_by
        adding = previous+",\n"+edited_by
        a.edited_by = adding
        a.save()
        messages.info(request, "Requisition Updated Successfully !!")

        action = "Edited"
        subject = action + " Job Requisition " + str(e.id)
        html_path = 'email.html'
        data = {'id': e.id, "created_date": e.requisition_date, "hc": e.hc_req, "department": e.department,
                "position": e.designation,
                "deadline": e.dead_line, "campaign": e.campaign, "user": request.user.profile.emp_name,
                "action": action,"status":e.request_status}
        email_template = get_template(html_path).render(data)
        to = [request.user.profile.emp_email, "aparna.ks@expertcallers.com"]
        email_msg = EmailMessage(subject,
                                 email_template, 'testm2063@gmail.com',
                                 to,
                                 reply_to=['qms@expertcallers.com'])
        email_msg.content_subtype = 'html'
        email_msg.send(fail_silently=False)
        designation = request.user.profile.emp_desi
        if designation in hr_list:
            return redirect("/erf/hr-dashboard")
        elif designation in am_mgr_list:
            return redirect("/erf/manager-dashboard")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")



@login_required
def jobRequisitionEditUpdate(request):
    if request.method == "POST":
        id = request.POST["id"]
        candidate_remark = request.POST["can_remark"]
        comments = request.POST["comments"]
        closure_date = request.POST.get("clos_date")
        candidate_name_1 = request.POST.get("cand_name_1")
        source_1 = request.POST.get("source_1")
        referral_emp_name_1 = request.POST.get("emp_name_1")
        referral_emp_id_1 = request.POST.get("emp_id_1")
        social_1 = request.POST.get("social_1")
        partner_1 = request.POST.get("partner_1")
        candidate_name_2 = request.POST.get("cand_name_2")
        source_2 = request.POST.get("source_2")
        referral_emp_name_2 = request.POST.get("emp_name_2")
        referral_emp_id_2 = request.POST.get("emp_id_2")
        social_2 = request.POST.get("social_2")
        partner_2 = request.POST.get("partner_2")
        candidate_name_3 = request.POST.get("cand_name_3")
        source_3 = request.POST.get("source_3")
        referral_emp_name_3 = request.POST.get("emp_name_3")
        referral_emp_id_3 = request.POST.get("emp_id_3")
        social_3 = request.POST.get("social_3")
        partner_3 = request.POST.get("partner_3")
        candidate_name_4 = request.POST.get("cand_name_4")
        source_4 = request.POST.get("source_4")
        referral_emp_name_4 = request.POST.get("emp_name_4")
        referral_emp_id_4 = request.POST.get("emp_id_4")
        social_4 = request.POST.get("social_4")
        partner_4 = request.POST.get("partner_4")
        candidate_name_5 = request.POST.get("cand_name_5")
        source_5 = request.POST.get("source_5")
        referral_emp_name_5 = request.POST.get("emp_name_5")
        referral_emp_id_5 = request.POST.get("emp_id_5")
        social_5 = request.POST.get("social_5")
        partner_5 = request.POST.get("partner_5")
        candidate_name_6 = request.POST.get("cand_name_6")
        source_6 = request.POST.get("source_6")
        referral_emp_name_6 = request.POST.get("emp_name_6")
        referral_emp_id_6 = request.POST.get("emp_id_6")
        social_6 = request.POST.get("social_6")
        partner_6 = request.POST.get("partner_6")
        candidate_name_7 = request.POST.get("cand_name_7")
        source_7 = request.POST.get("source_7")
        referral_emp_name_7 = request.POST.get("emp_name_7")
        referral_emp_id_7 = request.POST.get("emp_id_7")
        social_7 = request.POST.get("social_7")
        partner_7 = request.POST.get("partner_7")
        candidate_name_8 = request.POST.get("cand_name_8")
        source_8 = request.POST.get("source_8")
        referral_emp_name_8 = request.POST.get("emp_name_8")
        referral_emp_id_8 = request.POST.get("emp_id_8")
        social_8 = request.POST.get("social_8")
        partner_8 = request.POST.get("partner_8")
        candidate_name_9 = request.POST.get("cand_name_9")
        source_9 = request.POST.get("source_9")
        referral_emp_name_9 = request.POST.get("emp_name_9")
        referral_emp_id_9= request.POST.get("emp_id_9")
        social_9 = request.POST.get("social_9")
        partner_9 = request.POST.get("partner_9")
        candidate_name_10 = request.POST.get("cand_name_10")
        source_10 = request.POST.get("source_10")
        referral_emp_name_10 = request.POST.get("emp_name_10")
        referral_emp_id_10 = request.POST.get("emp_id_10")
        social_10 = request.POST.get("social_10")
        partner_10 = request.POST.get("partner_10")
        candidate_name_11 = request.POST.get("cand_name_11")
        source_11 = request.POST.get("source_11")
        referral_emp_name_11 = request.POST.get("emp_name_11")
        referral_emp_id_11 = request.POST.get("emp_id_11")
        social_11 = request.POST.get("social_11")
        partner_11 = request.POST.get("partner_11")
        candidate_name_12 = request.POST.get("cand_name_12")
        source_12 = request.POST.get("source_12")
        referral_emp_name_12 = request.POST.get("emp_name_12")
        referral_emp_id_12 = request.POST.get("emp_id_12")
        social_12 = request.POST.get("social_12")
        partner_12 = request.POST.get("partner_12")
        candidate_name_13 = request.POST.get("cand_name_13")
        source_13 = request.POST.get("source_13")
        referral_emp_name_13 = request.POST.get("emp_name_13")
        referral_emp_id_13 = request.POST.get("emp_id_13")
        social_13 = request.POST.get("social_13")
        partner_13 = request.POST.get("partner_13")
        candidate_name_14 = request.POST.get("cand_name_14")
        source_14 = request.POST.get("source_14")
        referral_emp_name_14 = request.POST.get("emp_name_14")
        referral_emp_id_14 = request.POST.get("emp_id_14")
        social_14 = request.POST.get("social_14")
        partner_14 = request.POST.get("partner_14")
        candidate_name_15 = request.POST.get("cand_name_15")
        source_15 = request.POST.get("source_15")
        referral_emp_name_15 = request.POST.get("emp_name_15")
        referral_emp_id_15 = request.POST.get("emp_id_15")
        social_15 = request.POST.get("social_15")
        partner_15 = request.POST.get("partner_15")
        candidate_name_16 = request.POST.get("cand_name_16")
        source_16 = request.POST.get("source_16")
        referral_emp_name_16 = request.POST.get("emp_name_16")
        referral_emp_id_16 = request.POST.get("emp_id_16")
        social_16 = request.POST.get("social_16")
        partner_16 = request.POST.get("partner_16")
        candidate_name_17 = request.POST.get("cand_name_17")
        source_17 = request.POST.get("source_17")
        referral_emp_name_17 = request.POST.get("emp_name_17")
        referral_emp_id_17 = request.POST.get("emp_id_17")
        social_17 = request.POST.get("social_17")
        partner_17 = request.POST.get("partner_17")
        candidate_name_18 = request.POST.get("cand_name_18")
        source_18 = request.POST.get("source_18")
        referral_emp_name_18 = request.POST.get("emp_name_18")
        referral_emp_id_18 = request.POST.get("emp_id_18")
        social_18 = request.POST.get("social_18")
        partner_18 = request.POST.get("partner_18")
        candidate_name_19 = request.POST.get("cand_name_19")
        source_19 = request.POST.get("source_19")
        referral_emp_name_19 = request.POST.get("emp_name_19")
        referral_emp_id_19 = request.POST.get("emp_id_19")
        social_19 = request.POST.get("social_19")
        partner_19 = request.POST.get("partner_19")
        candidate_name_20 = request.POST.get("cand_name_20")
        source_20 = request.POST.get("source_20")
        referral_emp_name_20 = request.POST.get("emp_name_20")
        referral_emp_id_20 = request.POST.get("emp_id_20")
        social_20 = request.POST.get("social_20")
        partner_20 = request.POST.get("partner_20")


        source_internal_emp_id_1 = request.POST.get("internal_emp_id_1")
        source_internal_campaign_name_1 = request.POST.get("internal_campaign_1")
        source_internal_emp_id_2 = request.POST.get("internal_emp_id_2")
        source_internal_campaign_name_2 = request.POST.get("internal_campaign_2")
        source_internal_emp_id_3 = request.POST.get("internal_emp_id_3")
        source_internal_campaign_name_3 = request.POST.get("internal_campaign_3")
        source_internal_emp_id_4 = request.POST.get("internal_emp_id_4")
        source_internal_campaign_name_4 = request.POST.get("internal_campaign_4")
        source_internal_emp_id_5 = request.POST.get("internal_emp_id_5")
        source_internal_campaign_name_5 = request.POST.get("internal_campaign_5")
        source_internal_emp_id_6 = request.POST.get("internal_emp_id_6")
        source_internal_campaign_name_6 = request.POST.get("internal_campaign_6")
        source_internal_emp_id_7 = request.POST.get("internal_emp_id_7")
        source_internal_campaign_name_7 = request.POST.get("internal_campaign_7")
        source_internal_emp_id_8 = request.POST.get("internal_emp_id_8")
        source_internal_campaign_name_8 = request.POST.get("internal_campaign_8")
        source_internal_emp_id_9 = request.POST.get("internal_emp_id_9")
        source_internal_campaign_name_9 = request.POST.get("internal_campaign_9")
        source_internal_emp_id_10 = request.POST.get("internal_emp_id_10")
        source_internal_campaign_name_10 = request.POST.get("internal_campaign_10")
        source_internal_emp_id_11 = request.POST.get("internal_emp_id_11")
        source_internal_campaign_name_11 = request.POST.get("internal_campaign_11")
        source_internal_emp_id_12 = request.POST.get("internal_emp_id_12")
        source_internal_campaign_name_12 = request.POST.get("internal_campaign_12")
        source_internal_emp_id_13 = request.POST.get("internal_emp_id_13")
        source_internal_campaign_name_13 = request.POST.get("internal_campaign_13")
        source_internal_emp_id_14 = request.POST.get("internal_emp_id_14")
        source_internal_campaign_name_14 = request.POST.get("internal_campaign_14")
        source_internal_emp_id_15 = request.POST.get("internal_emp_id_15")
        source_internal_campaign_name_15 = request.POST.get("internal_campaign_15")
        source_internal_emp_id_16 = request.POST.get("internal_emp_id_16")
        source_internal_campaign_name_16 = request.POST.get("internal_campaign_16")
        source_internal_emp_id_17 = request.POST.get("internal_emp_id_17")
        source_internal_campaign_name_17 = request.POST.get("internal_campaign_17")
        source_internal_emp_id_18 = request.POST.get("internal_emp_id_18")
        source_internal_campaign_name_18 = request.POST.get("internal_campaign_18")
        source_internal_emp_id_19 = request.POST.get("internal_emp_id_19")
        source_internal_campaign_name_19 = request.POST.get("internal_campaign_19")
        source_internal_emp_id_20 = request.POST.get("internal_emp_id_20")
        source_internal_campaign_name_20 = request.POST.get("internal_campaign_20")
        if source_internal_emp_id_1:
            source_internal_emp_name_1 = AllAgents.objects.get(emp_id=source_internal_emp_id_1).emp_name
        if source_internal_emp_id_2:
            source_internal_emp_name_2 = AllAgents.objects.get(emp_id=source_internal_emp_id_2).emp_name
        if source_internal_emp_id_3:
            source_internal_emp_name_3 = AllAgents.objects.get(emp_id=source_internal_emp_id_3).emp_name
        if source_internal_emp_id_4:
            source_internal_emp_name_4 = AllAgents.objects.get(emp_id=source_internal_emp_id_4).emp_name
        if source_internal_emp_id_5:
            source_internal_emp_name_5 = AllAgents.objects.get(emp_id=source_internal_emp_id_5).emp_name
        if source_internal_emp_id_6:
            source_internal_emp_name_6 = AllAgents.objects.get(emp_id=source_internal_emp_id_6).emp_name
        if source_internal_emp_id_7:
            source_internal_emp_name_7 = AllAgents.objects.get(emp_id=source_internal_emp_id_7).emp_name
        if source_internal_emp_id_8:
            source_internal_emp_name_8 = AllAgents.objects.get(emp_id=source_internal_emp_id_8).emp_name
        if source_internal_emp_id_9:
            source_internal_emp_name_9 = AllAgents.objects.get(emp_id=source_internal_emp_id_9).emp_name
        if source_internal_emp_id_10:
            source_internal_emp_name_10 = AllAgents.objects.get(emp_id=source_internal_emp_id_10).emp_name
        if source_internal_emp_id_11:
            source_internal_emp_name_11 = AllAgents.objects.get(emp_id=source_internal_emp_id_11).emp_name
        if source_internal_emp_id_12:
            source_internal_emp_name_12 = AllAgents.objects.get(emp_id=source_internal_emp_id_12).emp_name
        if source_internal_emp_id_13:
            source_internal_emp_name_13 = AllAgents.objects.get(emp_id=source_internal_emp_id_13).emp_name
        if source_internal_emp_id_14:
            source_internal_emp_name_14 = AllAgents.objects.get(emp_id=source_internal_emp_id_14).emp_name
        if source_internal_emp_id_15:
            source_internal_emp_name_15 = AllAgents.objects.get(emp_id=source_internal_emp_id_15).emp_name
        if source_internal_emp_id_16:
            source_internal_emp_name_16 = AllAgents.objects.get(emp_id=source_internal_emp_id_16).emp_name
        if source_internal_emp_id_17:
            source_internal_emp_name_17 = AllAgents.objects.get(emp_id=source_internal_emp_id_17).emp_name
        if source_internal_emp_id_18:
            source_internal_emp_name_18 = AllAgents.objects.get(emp_id=source_internal_emp_id_18).emp_name
        if source_internal_emp_id_19:
            source_internal_emp_name_19 = AllAgents.objects.get(emp_id=source_internal_emp_id_19).emp_name
        if source_internal_emp_id_20:
            source_internal_emp_name_20 = AllAgents.objects.get(emp_id=source_internal_emp_id_20).emp_name


        recruited_people = request.POST["rec_peo"]
        request_status = request.POST.get("req_status")
        if request_status == "Completed":
            request_status = "Waiting For Manager Approval"
        else:
            request_status = "Pending"

        e = JobRequisition.objects.get(id=id)

        if request_status == "Waiting For Manager Approval":
            e.initial_status = True
            e.closed_by = request.user.profile.emp_name
            e.closed_by_id = request.user.profile.emp_id

        if closure_date:
            e.closure_date = closure_date

        if candidate_name_1:
            e.candidate_name_1 = candidate_name_1
            e.source_1 = source_1
            e.source_emp_name_1 = referral_emp_name_1
            e.source_emp_id_1 = referral_emp_id_1
            if source_internal_emp_id_1:
                e.source_internal_emp_name_1 = source_internal_emp_name_1
            e.source_internal_emp_id_1 = source_internal_emp_id_1
            e.source_internal_campaign_name_1 = source_internal_campaign_name_1
            e.source_social_1 = social_1
            e.source_partners_1 = partner_1
        if candidate_name_2:
            e.candidate_name_2 = candidate_name_2
            e.source_2 = source_2
            e.source_emp_name_2 = referral_emp_name_2
            e.source_emp_id_2 = referral_emp_id_2
            if source_internal_emp_id_2:
                e.source_internal_emp_name_2 = source_internal_emp_name_2
            e.source_internal_emp_id_2 = source_internal_emp_id_2
            e.source_internal_campaign_name_2 = source_internal_campaign_name_2
            e.source_social_2 = social_2
            e.source_partners_2 = partner_2
        if candidate_name_3:
            e.candidate_name_3 = candidate_name_3
            e.source_3 = source_3
            e.source_emp_name_3 = referral_emp_name_3
            e.source_emp_id_3 = referral_emp_id_3
            if source_internal_emp_id_3:
                e.source_internal_emp_name_3 = source_internal_emp_name_3
            e.source_internal_emp_id_3 = source_internal_emp_id_3
            e.source_internal_campaign_name_3 = source_internal_campaign_name_3
            e.source_social_3 = social_3
            e.source_partners_3 = partner_3
        if candidate_name_4:
            e.candidate_name_4 = candidate_name_4
            e.source_4 = source_4
            e.source_emp_name_4 = referral_emp_name_4
            e.source_emp_id_4 = referral_emp_id_4
            if source_internal_emp_id_4:
                e.source_internal_emp_name_4 = source_internal_emp_name_4
            e.source_internal_emp_id_4 = source_internal_emp_id_4
            e.source_internal_campaign_name_4 = source_internal_campaign_name_4
            e.source_social_4 = social_4
            e.source_partners_4 = partner_4
        if candidate_name_5:
            e.candidate_name_5 = candidate_name_5
            e.source_5 = source_5
            e.source_emp_name_5 = referral_emp_name_5
            e.source_emp_id_5 = referral_emp_id_5
            if source_internal_emp_id_5:
                e.source_internal_emp_name_5 = source_internal_emp_name_5
            e.source_internal_emp_id_5 = source_internal_emp_id_5
            e.source_internal_campaign_name_5 = source_internal_campaign_name_5
            e.source_social_5 = social_5
            e.source_partners_5 = partner_5
        if candidate_name_6:
            e.candidate_name_6 = candidate_name_6
            e.source_6 = source_6
            e.source_emp_name_6 = referral_emp_name_6
            e.source_emp_id_6 = referral_emp_id_6
            e.source_internal_emp_name_6 = source_internal_emp_name_6
            e.source_internal_emp_id_6 = source_internal_emp_id_6
            e.source_internal_campaign_name_6 = source_internal_campaign_name_6
            e.source_social_6 = social_6
            e.source_partners_6 = partner_6
        if candidate_name_7:
            e.candidate_name_7 = candidate_name_7
            e.source_7 = source_7
            e.source_emp_name_7 = referral_emp_name_7
            e.source_emp_id_7 = referral_emp_id_7
            e.source_internal_emp_name_7 = source_internal_emp_name_7
            e.source_internal_emp_id_7 = source_internal_emp_id_7
            e.source_internal_campaign_name_7 = source_internal_campaign_name_7
            e.source_social_7 = social_7
            e.source_partners_7 = partner_7
        if candidate_name_8:
            e.candidate_name_8 = candidate_name_8
            e.source_8 = source_8
            e.source_emp_name_8 = referral_emp_name_8
            e.source_emp_id_8 = referral_emp_id_8
            e.source_internal_emp_name_8 = source_internal_emp_name_8
            e.source_internal_emp_id_8 = source_internal_emp_id_8
            e.source_internal_campaign_name_8 = source_internal_campaign_name_8
            e.source_social_8 = social_8
            e.source_partners_8 = partner_8
        if candidate_name_9:
            e.candidate_name_9 = candidate_name_9
            e.source_9 = source_9
            e.source_emp_name_9 = referral_emp_name_9
            e.source_emp_id_9 = referral_emp_id_9
            e.source_internal_emp_name_9 = source_internal_emp_name_9
            e.source_internal_emp_id_9 = source_internal_emp_id_9
            e.source_internal_campaign_name_9 = source_internal_campaign_name_9
            e.source_social_9 = social_9
            e.source_partners_9 = partner_9
        if candidate_name_10:
            e.candidate_name_10 = candidate_name_10
            e.source_10 = source_10
            e.source_emp_name_10 = referral_emp_name_10
            e.source_emp_id_10 = referral_emp_id_10
            e.source_internal_emp_name_10 = source_internal_emp_name_10
            e.source_internal_emp_id_10 = source_internal_emp_id_10
            e.source_internal_campaign_name_10 = source_internal_campaign_name_10
            e.source_social_10 = social_10
            e.source_partners_10 = partner_10
        if candidate_name_11:
            e.candidate_name_11 = candidate_name_11
            e.source_11 = source_11
            e.source_emp_name_11 = referral_emp_name_11
            e.source_emp_id_11 = referral_emp_id_11
            e.source_internal_emp_name_11 = source_internal_emp_name_11
            e.source_internal_emp_id_11 = source_internal_emp_id_11
            e.source_internal_campaign_name_11 = source_internal_campaign_name_11
            e.source_social_11 = social_11
            e.source_partners_11 = partner_11
        if candidate_name_12:
            e.candidate_name_12 = candidate_name_12
            e.source_12 = source_12
            e.source_emp_name_12 = referral_emp_name_12
            e.source_emp_id_12 = referral_emp_id_12
            e.source_internal_emp_name_12 = source_internal_emp_name_12
            e.source_internal_emp_id_12 = source_internal_emp_id_12
            e.source_internal_campaign_name_12 = source_internal_campaign_name_12
            e.source_social_12 = social_12
            e.source_partners_12 = partner_12
        if candidate_name_13:
            e.candidate_name_13 = candidate_name_13
            e.source_13 = source_13
            e.source_emp_name_13 = referral_emp_name_13
            e.source_emp_id_13 = referral_emp_id_13
            e.source_internal_emp_name_13 = source_internal_emp_name_13
            e.source_internal_emp_id_13 = source_internal_emp_id_13
            e.source_internal_campaign_name_13 = source_internal_campaign_name_13
            e.source_social_13 = social_13
            e.source_partners_13 = partner_13
        if candidate_name_14:
            e.candidate_name_14 = candidate_name_14
            e.source_14 = source_14
            e.source_emp_name_14 = referral_emp_name_14
            e.source_emp_id_14 = referral_emp_id_14
            e.source_internal_emp_name_14 = source_internal_emp_name_14
            e.source_internal_emp_id_14 = source_internal_emp_id_14
            e.source_internal_campaign_name_14 = source_internal_campaign_name_14
            e.source_social_14 = social_14
            e.source_partners_14 = partner_14
        if candidate_name_15:
            e.candidate_name_15 = candidate_name_15
            e.source_15 = source_15
            e.source_emp_name_15 = referral_emp_name_15
            e.source_emp_id_15 = referral_emp_id_15
            e.source_internal_emp_name_15 = source_internal_emp_name_15
            e.source_internal_emp_id_15 = source_internal_emp_id_15
            e.source_internal_campaign_name_15 = source_internal_campaign_name_15
            e.source_social_15 = social_15
            e.source_partners_15 = partner_15
        if candidate_name_16:
            e.candidate_name_16 = candidate_name_16
            e.source_16 = source_16
            e.source_emp_name_16 = referral_emp_name_16
            e.source_emp_id_16 = referral_emp_id_16
            e.source_internal_emp_name_16 = source_internal_emp_name_16
            e.source_internal_emp_id_16 = source_internal_emp_id_16
            e.source_internal_campaign_name_16 = source_internal_campaign_name_16
            e.source_social_16 = social_16
            e.source_partners_16 = partner_16
        if candidate_name_17:
            e.candidate_name_17 = candidate_name_17
            e.source_17 = source_17
            e.source_emp_name_17 = referral_emp_name_17
            e.source_emp_id_17 = referral_emp_id_17
            e.source_internal_emp_name_17 = source_internal_emp_name_17
            e.source_internal_emp_id_17 = source_internal_emp_id_17
            e.source_internal_campaign_name_17 = source_internal_campaign_name_17
            e.source_social_17 = social_17
            e.source_partners_17 = partner_17
        if candidate_name_18:
            e.candidate_name_18 = candidate_name_18
            e.source_18 = source_18
            e.source_emp_name_18 = referral_emp_name_18
            e.source_emp_id_18 = referral_emp_id_18
            e.source_internal_emp_name_18 = source_internal_emp_name_18
            e.source_internal_emp_id_18 = source_internal_emp_id_18
            e.source_internal_campaign_name_18 = source_internal_campaign_name_18
            e.source_social_18 = social_18
            e.source_partners_18 = partner_18
        if candidate_name_19:
            e.candidate_name_19 = candidate_name_19
            e.source_19 = source_19
            e.source_emp_name_19 = referral_emp_name_19
            e.source_emp_id_19 = referral_emp_id_19
            e.source_internal_emp_name_19 = source_internal_emp_name_19
            e.source_internal_emp_id_19 = source_internal_emp_id_19
            e.source_internal_campaign_name_19 = source_internal_campaign_name_19
            e.source_social_19 = social_19
            e.source_partners_19 = partner_19
        if candidate_name_20:
            e.candidate_name_20 = candidate_name_20
            e.source_20 = source_20
            e.source_emp_name_20 = referral_emp_name_20
            e.source_emp_id_20 = referral_emp_id_20
            e.source_internal_emp_name_20 = source_internal_emp_name_20
            e.source_internal_emp_id_20 = source_internal_emp_id_20
            e.source_internal_campaign_name_20 = source_internal_campaign_name_20
            e.source_social_20 = social_20
            e.source_partners_20 = partner_20

        e.recruited_people = recruited_people
        e.request_status = request_status
        e.candidate_remark = candidate_remark
        e.save()
        a = Tickets.objects.get(job_requisition_id=id)
        now_datetime = datetime.datetime.now().strftime('%b %d,%Y %H:%M:%S')
        edited_name = request.user.profile.emp_name
        edited_id = request.user.profile.emp_id
        edited_by = str([now_datetime, edited_name, edited_id, comments])
        previous = a.edited_by
        adding = previous+",\n"+edited_by
        a.edited_by = adding
        a.save()
        messages.info(request, "Requisition Updated Successfully !!")

        action = "Updated"
        subject = action + " Job Requisition " + str(e.id)
        html_path = 'email.html'
        data = {'id': e.id, "created_date": e.requisition_date, "hc": e.hc_req, "department": e.department,
                "position": e.designation,
                "deadline": e.dead_line, "campaign": e.campaign, "user": request.user.profile.emp_name,
                "action": action,"status":e.request_status}
        email_template = get_template(html_path).render(data)
        creater_id = e.created_by_id
        creater_email = Profile.objects.get(emp_id=creater_id).emp_email
        to = [request.user.profile.emp_email, "aparna.ks@expertcallers.com",creater_email]
        email_msg = EmailMessage(subject,
                                 email_template, 'testm2063@gmail.com',
                                 to,
                                 reply_to=['qms@expertcallers.com'])
        email_msg.content_subtype = 'html'
        email_msg.send(fail_silently=False)

        if request.user.profile.emp_desi in hr_list:
            return redirect("/erf/hr-dashboard")
        elif request.user.profile.emp_desi in am_mgr_list:
            return redirect("/erf/manager-dashboard")
        else:
            messages.info(request, "Invalid Request. You have been logged out :)")
            return redirect("/erf/")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated! Please login with new password.')

            user = request.user
            user.profile.pc = True
            user.save()
            user.profile.save()
            logout(request)
            return redirect('/erf/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'settings.html', {'form': form})



# create User
def createUserandProfile(request):
    emp = Employee.objects.all()
    for i in emp:
        user = User.objects.filter(username=i.emp_id)
        if user.exists():
            print(i.emp_name + ' ' + 'exist')
        else:
            usr = User.objects.create_user(username=i.emp_id, password=str(i.emp_id))

            profile = Profile.objects.create(
                emp_id = i.emp_id,emp_name = i.emp_name, emp_desi = i.emp_desi,
                emp_rm1 = i.emp_rm1, emp_rm1_id = i.emp_rm1_id,emp_rm2 = i.emp_rm2, emp_rm2_id = i.emp_rm2_id,emp_rm3 = i.emp_rm3,
                emp_rm3_id=i.emp_rm3_id,
                emp_process = i.emp_process, user_id = usr.id
                                          )
            profile.save()
            usr.save()
            print('created'+ i.emp_name)

def approval(request):
    if request.method == "POST":
        id = request.POST["id"]
        response = request.POST["response"]
        e = JobRequisition.objects.get(id=id)
        a = Tickets.objects.get(job_requisition_id=id)
        if response == "Approve":
            e.final_status = True
            e.request_status = "Approved and Complete"
            comment = "Approved and Complete"
            action = "Approved"
        if response == "Reject":
            e.initial_status = False
            e.request_status = "Rejected by Manager"
            comment = "Rejected by Manager"
            action = "Rejected"
        e.save()
        now_datetime = datetime.datetime.now().strftime('%b %d,%Y %H:%M:%S')
        edited_name = request.user.profile.emp_name
        edited_id = request.user.profile.emp_id
        edited_by = str([now_datetime, edited_name, edited_id, comment])
        previous = a.edited_by
        adding = previous + ",\n" + edited_by
        a.edited_by = adding
        a.save()
        messages.info(request,"Changes have been made successfully!")

        subject = action + " Job Requisition " + str(e.id)
        html_path = 'email.html'
        data = {'id': e.id, "created_date": e.requisition_date, "hc": e.hc_req, "department": e.department,
                "position": e.designation,
                "deadline": e.dead_line, "campaign": e.campaign, "user": request.user.profile.emp_name,
                "action": action, "status": e.request_status}
        email_template = get_template(html_path).render(data)
        creater_id = e.created_by_id
        creater_email = Profile.objects.get(emp_id=creater_id).emp_email
        to = [request.user.profile.emp_email, "aparna.ks@expertcallers.com", creater_email]
        email_msg = EmailMessage(subject,
                                 email_template, 'testm2063@gmail.com',
                                 to,
                                 reply_to=['qms@expertcallers.com'])
        email_msg.content_subtype = 'html'
        email_msg.send(fail_silently=False)
        if request.user.profile.emp_desi in hr_list:
            return redirect("/erf/hr-dashboard")
        elif request.user.profile.emp_desi in am_mgr_list:
            return redirect("/erf/manager-dashboard")
        else:
            messages.info(request, "Invalid Request. You have been logged out :)")
            return redirect("/erf/")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")

def testFun(request):
    subject = "Created Job Requisition"
    html_path = 'email.html'
    data = {'id': "47"}
    email_template = get_template(html_path).render(data)
    to = ["testm2063@gmail.com"]
    email_msg = EmailMessage(subject,
                             email_template, 'testm2063@gmail.com',
                             to,
                             reply_to=['qms@expertcallers.com'])
    email_msg.content_subtype = 'html'
    email_msg.send(fail_silently=False)
    return render(request,"email.html")
