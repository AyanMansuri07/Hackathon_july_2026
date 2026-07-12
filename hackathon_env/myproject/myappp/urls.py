from django.urls import path
from . import views

urlpatterns=[

    path('',views.login,name="login"),

    path('register/',views.register,name="register"),

    path('verify-otp/',views.verify_otp,name="verify_otp"),

    path('logout/',views.logout,name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("employee-dashboard/", views.employee_dashboard, name="employee_dashboard"),

    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    path("asset-manager-dashboard/", views.asset_manager_dashboard, name="asset_manager_dashboard"),

    path("department-head-dashboard/", views.department_head_dashboard, name="department_head_dashboard"),



]