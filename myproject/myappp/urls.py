from django.urls import path
from . import views


urlpatterns = [

    # Login/Register
    path(
        '',
        views.login,
        name="login"
    ),


    path(
        'register/',
        views.register,
        name="register"
    ),


    path(
        'verify-otp/',
        views.verify_otp,
        name="verify_otp"
    ),


    path(
        'logout/',
        views.logout,
        name="logout"
    ),



    # Dashboards

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),


    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),


    path(
        "asset-manager-dashboard/",
        views.asset_manager_dashboard,
        name="asset_manager_dashboard"
    ),


    path(
        "department-head-dashboard/",
        views.department_head_dashboard,
        name="department_head_dashboard"
    ),


    path(
        "employee-dashboard/",
        views.employee_dashboard,
        name="employee_dashboard"
    ),



    # Employee

    path(
        "employee-profile/",
        views.employee_profile,
        name="employee_profile"
    ),


    path(
        "employee-notifications/",
        views.employee_notifications,
        name="employee_notifications"
    ),


    path(
        "employee-assets/",
        views.employee_assets,
        name="employee_assets"
    ),



    # Asset Manager

    path(
        "add-asset/",
        views.add_asset,
        name="add_asset"
    ),


    path(
        "asset-list/",
        views.asset_list,
        name="asset_list"
    ),


    path(
        "asset-allocation/",
        views.asset_allocation,
        name="asset_allocation"
    ),

    path(
    "department-employees/",
    views.department_employees,
    name="department_employees"
),

path(
"request-asset/",
views.request_asset,
name="request_asset"
),

path(
    "department-asset-requests/",
    views.department_asset_requests,
    name="department_asset_requests"
),

]