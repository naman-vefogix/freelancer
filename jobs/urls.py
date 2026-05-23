from django.urls import path
from . import views

urlpatterns = [
    
    # core django 
    path('', views.job_list, name = 'job_list'),
    path('create/', views.create_job, name='create_job'),
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('<int:job_id>/applications/', views.view_applications, name='view_applications'),

    #rest api -> APIViews
    path('api/jobs/APIViews/jobs/', views.JobAPIView.as_view(),name = "jobs_APIViews" ),
    path('api/jobs/APIViews/jobs/<int:id>/', views.DetailJobAPIView.as_view(), name="jobs_details_APIView"),

    #rest api paths -> generics
    path('api/jobs', views.JobListCreateAPIView.as_view(),name = "api_jobs"),
    path('api/jobs/<int:id>', views.JobDetailAPIView.as_view(), name = "api_job_detail"),

    #rest api -> manual
    # path('api/job-list',views.api_job_list,name='api_job_list'), # fnction based view
    path('api/job-list',views.JobListAPIView.as_view(),name='api_job_list'), # class based view
    path('api/job-list/<int:job_id>',views.api_job_detail,name='api_job_detail' ),
    path('api/job-create', views.api_create_job, name='api_create_job'),
    path('api/job/<int:job_id>/update',views.api_update_job,name='api_update_job'),

    # dashboards
    # path('client_dashboard/', views.client_dashboard, name='client_dashboard'),
    # path('freelance_setup/',views.freelance_setup, name='freelance_setup'),
]
