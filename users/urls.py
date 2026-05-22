from django.urls import path
from .views import signup_view, home_view, client_dashboard, freelancer_setup, login_redirect_view

urlpatterns = [
    path('', home_view, name = 'home'),
    path('signup/', signup_view, name='signup'),
    path('client_dashboard', client_dashboard, name = "client_dashboard" ),
    path('freelancer_setup', freelancer_setup, name="freelancer_setup"),
    path('login_redirect/', login_redirect_view, name="login_redirect")
]

