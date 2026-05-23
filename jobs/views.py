from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job, Applications
from .forms import JobForm, ApplicationForm
from notifications.services import create_notification

# rest imports
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import JobSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

# rest imports - views
from rest_framework.views import APIView

# test postman - will explicit mention user
from users.models import CustomUser 

## rest api

# APIView (used here)

class JobAPIView(APIView):
    def get(self,request):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs,many = True)
        return Response(serializer.data)

    def post(self,request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client = request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DetailJobAPIView(APIView):
    def get(self, request, id):
        job = get_object_or_404(Job, id=id)
        serializer = JobSerializer(job)
        return Response(serializer.data)

    def put(self, request, id):
        job = get_object_or_404(Job, id=id)
        serializer = JobSerializer(job,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, id):
        job = get_object_or_404(Job, id=id)
        serializer = JobSerializer(job,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        job = get_object_or_404(Job, id=id)
        job.delete()
        return Response({"message": "Deleted successfully"},status=status.HTTP_204_NO_CONTENT)

#using generics
class JobListAPIView(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

class JobListCreateAPIView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

class JobDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = 'id'

# manual REST APIs 
@api_view(['GET'])
def api_job_list(request):
    job = Job.objects.all()
    serializer = JobSerializer(job,many = True)
    return Response(serializer.data)

@api_view(['GET'])
def api_job_detail(request,job_id = None):
    try:
        job = Job.objects.get(id = job_id)
    except Job.DoesNotExist:
        return Response({'error':"job not found"}, status=status.HTTP_404_NOT_FOUND)
        
    serializer = JobSerializer(job)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated]) #
def api_create_job(request):
    serializer = JobSerializer(data = request.data)
    if serializer.is_valid():
        dummy_user = CustomUser.objects.first() # explicit user mentioned here
        # serializer.save(client = request.user)
        serializer.save(client = dummy_user) # have to change dummy user here 
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def api_update_job(request, job_id):
    try:
        job = Job.objects.get(id = job_id)
    except Job.DoesNotExist:
        return Response({"error" : "job not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = JobSerializer(job, data=request.data,partial = True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


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

@login_required
def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

@login_required
def view_applications(request, job_id):
    job = get_object_or_404(Job, id = job_id, client = request.user)
    applications = job.applications.all()
    return render(request, 'jobs/view_applications.html', {'job': job, 'applications': applications})