from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job, Applications
from .forms import JobForm, ApplicationForm
from notifications.services import create_notification

# Create your views here.

@login_required
def create_job(request):
    if not request.user.is_verified or request.user.role != 'client':
        return render(request, 'users/not_verified.html', {"username" : request.user.username})
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid() :  
            job = form.save(commit=False)
            job.client = request.user
            job.save()
            return redirect('client_dashboard')
    else:
        form = JobForm()
    return render(request, 'jobs/create_job.html',{'form' : form})

@login_required
def apply_job(request, job_id):

    if not request.user.is_verified or request.user.role != 'freelancer':
        return render(
            request,
            'users/not_verified.html',
            {"username": request.user.username}
        )

    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":

        form = ApplicationForm(request.POST)

        if form.is_valid():

            application = form.save(commit=False)

            application.job = job
            application.freelancer = request.user

            application.save()

            print("APPLICATION SAVED")

            create_notification(
                job.client,
                "New Job Application",
                f"{request.user.username} applied for your job: {job.title}"
            )

            print("NOTIFICATION FUNCTION CALLED")

            return redirect('freelancer_setup')

    else:
        form = ApplicationForm()

    return render(
        request,
        'jobs/apply_job.html',
        {
            'form': form,
            'job': job
        }
    )


# @login_required
# def apply_job(request, job_id):
#     if not request.user.is_verified or request.user.role != 'freelancer':
#         return render(request, 'users/not_verified.html', {"username" : request.user.username})

#     job = get_object_or_404(Job, id = job_id)
#     if request.method == "POST":
#         form = ApplicationForm(request.POST)
#         if form.is_valid():
#             application = form.save(commit=False)
#             application.job = job
#             application.freelancer = request.user
#             application.save()
#             return redirect('freelancer_setup')
#     else:
#         form = ApplicationForm()
#     return render(request, 'jobs/apply_job.html', {'form' : form, 'job': job})

# @login_required
# def client_dashboard(request):
#     if request.user.role != 'client':
#         return render(request, 'users/not_verified.html')
#     jobs = Job.objects.filter(client = request.user).order_by('-created_at')
#     return render(request, 'users/client_dashboard.html', {'jobs' : jobs})

# @login_required
# def freelance_setup(request):
#     if request.user.role != 'freelancer':
#         return render(request, 'users/not_verified.html')

#     jobs = Job.objects.all().order_by('-created_at')
#     applications = Applications.objects.filter(freelancer=request.user).order_by('-applied_at')

#     print(jobs)
#     print(applications)

#     return render(request, 'users/freelancer_setup.html', {
#         'jobs': jobs,
#         'applications': applications,
#         'username': request.user.username
#     })


@login_required
def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

@login_required
def view_applications(request, job_id):
    job = get_object_or_404(Job, id = job_id, client = request.user)
    applications = job.applications.all()
    return render(request, 'jobs/view_applications.html', {'job': job, 'applications': applications})