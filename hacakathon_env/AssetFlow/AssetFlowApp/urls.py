from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('otp/', views.otp_verify_view, name='otp_verify'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('', views.login_view, name='home'),
]
