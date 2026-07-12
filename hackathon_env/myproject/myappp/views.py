import random

from django.shortcuts import render,redirect

from django.core.mail import send_mail

from django.conf import settings

from .models import *



import random
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .models import *


def register(request):

    # Get all departments (always)
    departments = Department.objects.all()

    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        employee_code = request.POST.get('employee_code')
        role = request.POST.get('role')
        department = request.POST.get('department')

        # Password Match Validation
        if password != confirm_password:

            context = {
                "departments": departments,
                "e_msg": "Password and Confirm Password do not match."
            }

            return render(request, "myapp/register.html", context)

        # Email Already Exists
        if User.objects.filter(email=email).exists():

            context = {
                "departments": departments,
                "e_msg": "Email already registered. Please Login."
            }

            return render(request, "myapp/register.html", context)

        # Employee Code Exists
        if Employee.objects.filter(employee_code=employee_code).exists():

            context = {
                "departments": departments,
                "e_msg": "Employee Code already exists."
            }

            return render(request, "myapp/register.html", context)

        # Generate OTP
        otp = random.randint(100000, 999999)

        # Store Data in Session
        request.session['first_name'] = first_name
        request.session['last_name'] = last_name
        request.session['email'] = email
        request.session['contact'] = contact
        request.session['password'] = password
        request.session['employee_code'] = employee_code
        request.session['role'] = role
        request.session['department'] = department
        request.session['otp'] = otp

        # Send OTP Email
        send_mail(
            subject="AssetFlow ERP - Email Verification",
            message=f"""
Hello {first_name},

Welcome to AssetFlow ERP.

Your OTP for Email Verification is:

{otp}

Do not share this OTP with anyone.

Thank You,
AssetFlow ERP Team
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )

        return redirect("verify_otp")

    context = {
        "departments": departments
    }

    return render(request, "myapp/register.html", context)


def verify_otp(request):

    # Check if OTP exists in session
    if 'otp' not in request.session:
        return redirect("register")

    if request.method == "POST":

        uotp = request.POST.get("otp")

        if str(uotp) == str(request.session.get("otp")):

            user = User.objects.create(
                email=request.session['email'],
                password=request.session['password'],
                role=request.session['role'],
                otp=request.session['otp']
            )

            department = Department.objects.get(
                id=request.session['department']
            )

            Employee.objects.create(
                user=user,
                first_name=request.session['first_name'],
                last_name=request.session['last_name'],
                contact_no=request.session['contact'],
                employee_code=request.session['employee_code'],
                department=department
            )

            # Clear session data
            request.session.flush()

            return render(request, "myapp/login.html", {
                "s_msg": "Registration Successful. Please Login."
            })

        else:

            return render(request, "myapp/verify_otp.html", {
                "e_msg": "Invalid OTP"
            })

    return render(request, "myapp/verify_otp.html")


def login(request):

    if request.method == "POST":

        email = request.POST['email']
        password = request.POST['password']

        try:

            user = User.objects.get(
                email=email,
                password=password
            )

            request.session['uid'] = user.id
            request.session['email'] = user.email
            request.session['role'] = user.role

            if user.role == "ADMIN":

                return redirect("admin_dashboard")

            elif user.role == "ASSET_MANAGER":

                return redirect("asset_manager_dashboard")

            elif user.role == "DEPARTMENT_HEAD":

                return redirect("department_head_dashboard")

            elif user.role == "EMPLOYEE":

                return redirect("employee_dashboard")

        except User.DoesNotExist:

            context = {

                "e_msg": "Invalid Email or Password"

            }

            return render(request, "myapp/login.html", context)

    return render(request, "myapp/login.html")


def logout(request):

    del request.session['uid']
    del request.session['email']
    del request.session['role']

    return redirect("login")


def dashboard(request):

    if 'uid' not in request.session:
        return redirect("login")

    user = User.objects.get(id=request.session['uid'])

    employee = Employee.objects.get(user=user)

    context = {
        "user": user,
        "employee": employee,
    }

    return render(request, "myapp/dashboard.html", context)


def admin_dashboard(request):

    if 'uid' not in request.session:
        return redirect("login")

    user = User.objects.get(id=request.session['uid'])

    return render(request, "myapp/admin_dashboard.html", {"user": user})


def asset_manager_dashboard(request):

    if 'uid' not in request.session:
        return redirect("login")

    user = User.objects.get(id=request.session['uid'])

    return render(request, "myapp/asset_manager_dashboard.html", {"user": user})


def department_head_dashboard(request):

    if 'uid' not in request.session:
        return redirect("login")

    user = User.objects.get(id=request.session['uid'])

    return render(request, "myapp/department_head_dashboard.html", {"user": user})




def employee_dashboard(request):

    if 'uid' not in request.session:

        return redirect("login")

    user = User.objects.get(id=request.session['uid'])

    employee = Employee.objects.get(user=user)

    context = {

        "user": user,
        "employee": employee

    }

    return render(request, "myapp/employee_dashboard.html", context)