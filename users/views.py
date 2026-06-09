from django.shortcuts import render, redirect
from .forms import SignupForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

# Import models from jobs app
from jobs.models import Job, Applications
from notifications.models import Notification
from activity.models import UserActivity

from django.utils import timezone

# Create your views here.
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            login(request, user)
            # UserActivity.objects.create(
            #     user=request.user,
            #     event_type="user",
            #     action_type="signup",
            #     metadata={
            #         "role": request.user.role
            #     }
            # )
            if user.role == 'client':
                return redirect('client_dashboard')
            elif user.role == 'freelancer':
                return redirect('freelancer_setup')
            else:
                return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'users/signup.html', {"form": form})

def home_view(request):
    return render(request, 'users/home.html')


@login_required
def client_dashboard(request):
    if request.user.role != 'client':
        return redirect('freelancer_setup')
    jobs = Job.objects.filter(client = request.user).order_by('-created_at')
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_notifications_count = notifications.count()
    print(notifications.count())
    return render(request, 'users/client_dashboard.html', {'jobs' : jobs, 'notifications': notifications,  'unread_notifications_count': unread_notifications_count})


@login_required
def freelancer_setup(request):
    if request.user.role != 'freelancer':
        return redirect('client_dashboard')

    jobs = Job.objects.all().order_by('-created_at')
    applications = Applications.objects.filter(freelancer=request.user).order_by('-applied_at')
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_notifications_count = notifications.count()
    print(jobs)
    print(applications)

    return render(request, 'users/freelancer_setup.html', {
        'jobs': jobs,
        'applications': applications,
        'username': request.user.username,
        'notifications': notifications,  
        'unread_notifications_count': unread_notifications_count
    })


@login_required
def login_redirect_view(request):
    # UserActivity.objects.create(
    #     user=request.user,
    #     event_type="user",
    #     action_type="login",
    #     metadata={
    #         "role": request.user.role
    #     }
    # )
    if request.user.role == "client":
        return redirect("client_dashboard")
    elif request.user.role == "freelancer":
        return redirect("freelancer_setup")
    return redirect("home")

