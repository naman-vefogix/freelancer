from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name = 'job_list'),
    path('create/', views.create_job, name='create_job'),
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('<int:job_id>/applications/', views.view_applications, name='view_applications'),

    #rest api paths
    path('api/',views.api_job_list,name='api_job_list'),

    # path('client_dashboard/', views.client_dashboard, name='client_dashboard'),
    # path('freelance_setup/',views.freelance_setup, name='freelance_setup'),
]
