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



    path("departments/", views.manage_departments, name="manage_departments"),
    path("employees/", views.manage_employees, name="manage_employees"),
    path("categories/", views.manage_categories, name="manage_categories"),
    path("assets/", views.manage_assets, name="manage_assets"),

    path("allocations/", views.allocate_asset, name="allocate_asset"),
    path("bookings/", views.manage_bookings, name="manage_bookings"),
    path("maintenance/", views.manage_maintenance, name="manage_maintenance"),
    path("audits/", views.manage_audits, name="manage_audits"),

]
