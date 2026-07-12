from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import *
import random






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

            request.session.flush()

            messages.success(

                request,

                "Registration Successful. Please Login."

            )

            return redirect("login")

        else:

            return render(

                request,

                "myapp/verify_otp.html",

                {

                    "e_msg": "Invalid OTP"

                }

            )

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


from django.db.models import Count


def asset_manager_dashboard(request):

    if 'uid' not in request.session:
        return redirect("login")


    user = User.objects.get(
        id=request.session['uid']
    )


    context = {


        "user": user,


        # Total assets

        "total_assets":
            Asset.objects.count(),



        # Available assets

        "available_assets":
            Asset.objects.filter(
                asset_status="AVAILABLE"
            ).count(),



        # Allocated assets

        "allocated_assets":
            Asset.objects.filter(
                asset_status="ALLOCATED"
            ).count(),



        # Damaged assets

        "damaged_assets":
            Asset.objects.filter(
                asset_status="DAMAGED"
            ).count(),



        # Maintenance assets

        "maintenance_assets":
            Asset.objects.filter(
                asset_status="MAINTENANCE"
            ).count(),



        # Total employees

        "employees":
            Employee.objects.count(),

    }



    return render(
        request,
        "myapp/asset_manager_dashboard.html",
        context
    )


def department_head_dashboard(request):

    if 'uid' not in request.session:
        return redirect("login")


    user = User.objects.get(
        id=request.session['uid']
    )


    employee = Employee.objects.get(
        user=user
    )


    context = {

        "user":user,
        "employee":employee

    }


    return render(
        request,
        "myapp/department_head_dashboard.html",
        context
    )

def department_employees(request):

    if 'uid' not in request.session:
        return redirect("login")


    user = User.objects.get(
        id=request.session['uid']
    )


    # Get logged in department head details

    head = Employee.objects.get(
        user=user
    )


    # Get only same department employees

    employees = Employee.objects.filter(
        department=head.department
    )


    context = {

        "employees":employees,

        "department":head.department

    }


    return render(
        request,
        "myapp/department_employees.html",
        context
    )


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


def employee_profile(request):

    if 'uid' not in request.session:

        return redirect("login")


    uid = request.session['uid']


    user = User.objects.get(
        id=uid
    )


    employee = Employee.objects.get(
        user=user
    )


    context = {

        "user": user,

        "employee": employee

    }


    return render(
        request,
        "myapp/employee_profile.html",
        context
    )

def employee_notifications(request):

    if 'uid' not in request.session:

        return redirect("login")


    user = User.objects.get(
        id=request.session['uid']
    )


    employee = Employee.objects.get(
        user=user
    )


    context = {

        "user": user,

        "employee": employee,

    }


    return render(
        request,
        "myapp/employee_notifications.html",
        context
    )

def employee_assets(request):

    if 'uid' not in request.session:

        return redirect("login")


    user = User.objects.get(
        id=request.session['uid']
    )


    employee = Employee.objects.get(
        user=user
    )


    # Get assets allocated to logged in employee

    allocations = AssetAllocation.objects.filter(
        employee=employee,
        status="ALLOCATED"
    )


    context = {

        "user": user,

        "employee": employee,

        "allocations": allocations

    }


    return render(
        request,
        "myapp/employee_assets.html",
        context
    )


def add_asset(request):

    if 'uid' not in request.session:
        return redirect("login")


    categories = AssetCategory.objects.all()



    if request.method=="POST":


        category = AssetCategory.objects.get(
            id=request.POST.get('category')
        )



        asset = Asset.objects.create(


            asset_name=request.POST.get('asset_name'),


            asset_code=request.POST.get('asset_code'),


            category=category,


            brand=request.POST.get('brand'),


            model_number=request.POST.get('model_number'),


            serial_number=request.POST.get('serial_number'),


            purchase_date=request.POST.get('purchase_date'),


            purchase_price=request.POST.get('purchase_price'),


            warranty_expiry=request.POST.get('warranty_expiry'),



            asset_status="AVAILABLE",



            condition=request.POST.get('condition')
            or "NEW",



            location=request.POST.get('location'),


            description=request.POST.get('description'),


            asset_image=request.FILES.get('asset_image')

        )



        # increase category count

        category.no_of_asset += 1

        category.save()



        return redirect(
            "asset_list"
        )



    return render(
        request,
        "myapp/add_asset.html",
        {
            "categories":categories
        }
    )
def asset_allocation(request):

    if 'uid' not in request.session:
        return redirect("login")


    assets = Asset.objects.filter(
        asset_status="AVAILABLE"
    )

    employees = Employee.objects.all()


    if request.method == "POST":

        asset_id = request.POST.get("asset")

        employee_id = request.POST.get("employee")

        remarks = request.POST.get("remarks")


        asset = Asset.objects.get(
            id=asset_id
        )

        employee = Employee.objects.get(
            id=employee_id
        )


        AssetAllocation.objects.create(

            asset=asset,

            employee=employee,

            allocated_by=User.objects.get(
                id=request.session['uid']
            ),

            remarks=remarks

        )


        # Update asset status

        asset.asset_status="ALLOCATED"

        asset.save()


        return redirect("asset_manager_dashboard")



    context={

        "assets":assets,

        "employees":employees

    }


    return render(
        request,
        "myapp/asset_allocation.html",
        context
    )


def asset_list(request):

    if 'uid' not in request.session:
        return redirect("login")


    assets = Asset.objects.all()


    context = {

        "assets": assets

    }


    return render(
        request,
        "myapp/asset_list.html",
        context
    )


from .models import AssetRequest,Employee,User

def request_asset(request):

    if 'uid' not in request.session:
        return redirect("login")


    if request.method == "POST":

        asset_name = request.POST.get('asset_name')

        reason = request.POST.get('reason')


        user = User.objects.get(
            id=request.session['uid']
        )


        employee = Employee.objects.get(
            user=user
        )


        AssetRequest.objects.create(

            employee=employee,

            asset_name=asset_name,

            reason=reason

        )


        context = {

            "msg":"Asset Request Sent Successfully"

        }


        return render(
            request,
            "myapp/request_asset.html",
            context
        )


    return render(
        request,
        "myapp/request_asset.html"
    )

def department_asset_requests(request):

    if 'uid' not in request.session:
        return redirect("login")


    user = User.objects.get(
        id=request.session['uid']
    )


    head = Employee.objects.get(
        user=user
    )


    requests = AssetRequest.objects.filter(
        employee__department=head.department
    )


    context = {

        "requests": requests

    }


    return render(
        request,
        "myapp/department_asset_requests.html",
        context
    )