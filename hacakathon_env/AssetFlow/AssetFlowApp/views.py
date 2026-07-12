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

            return render(request, "AssetFlowApp/register.html", context)

        # Email Already Exists
        if User.objects.filter(email=email).exists():

            context = {
                "departments": departments,
                "e_msg": "Email already registered. Please Login."
            }

            return render(request, "AssetFlowApp/register.html", context)

        # Employee Code Exists
        if Employee.objects.filter(employee_code=employee_code).exists():

            context = {
                "departments": departments,
                "e_msg": "Employee Code already exists."
            }

            return render(request, "AssetFlowApp/register.html", context)

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

    return render(request, "AssetFlowApp/register.html", context)


def verify_otp(request):

    # Check if OTP exists in session
    if 'otp' not in request.session:
        return redirect("login")

    if request.method == "POST":

        uotp = request.POST.get("otp")

        if str(uotp) == str(request.session.get("otp")):
            
            # Check if this is a password reset flow
            if request.session.get("otp_context") == "reset":
                # OTP is verified, now allow password reset
                request.session['otp_verified'] = True
                return render(request, "AssetFlowApp/verify_otp.html", {
                    "show_reset_form": True,
                    "s_msg": "OTP Verified. Please enter your new password."
                })

            # Otherwise, this is a registration flow
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

            return render(request, "AssetFlowApp/login.html", {
                "s_msg": "Registration Successful. Please Login."
            })

        else:

            return render(request, "AssetFlowApp/verify_otp.html", {
                "e_msg": "Invalid OTP"
            })

    return render(request, "AssetFlowApp/verify_otp.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if User.objects.filter(email=email).exists():
            otp = random.randint(100000, 999999)
            request.session['otp'] = otp
            request.session['email'] = email
            request.session['otp_context'] = 'reset'
            
            # Send OTP Email
            try:
                send_mail(
                    subject="AssetFlow ERP - Password Reset",
                    message=f"Hello,\n\nYour OTP for password reset is: {otp}\n\nDo not share this with anyone.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False
                )
            except:
                pass # Fail silently for hackathon if email is not configured perfectly
                
            return redirect("verify_otp")
        else:
            return render(request, "AssetFlowApp/login.html", {"e_msg": "Email not found."})
    return redirect("login")

def reset_password(request):
    if request.method == "POST":
        if not request.session.get('otp_verified'):
            return redirect("login")
            
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        if password != confirm_password:
            return render(request, "AssetFlowApp/verify_otp.html", {
                "show_reset_form": True,
                "e_msg": "Passwords do not match."
            })
            
        email = request.session.get("email")
        user = User.objects.get(email=email)
        user.password = password
        user.save()
        
        request.session.flush()
        return render(request, "AssetFlowApp/login.html", {"s_msg": "Password reset successful. Please Login."})
        
    return redirect("login")

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

            return render(request, "AssetFlowApp/login.html", context)

    return render(request, "AssetFlowApp/login.html")


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

    return render(request, "AssetFlowApp/dashboard.html", context)


def admin_dashboard(request):

    if 'uid' not in request.session:
        return redirect("login")

    user = User.objects.get(id=request.session['uid'])

    # Aggregate Metrics
    total_employees = Employee.objects.count()
    total_departments = Department.objects.count()
    total_assets = Asset.objects.count()
    available_assets = Asset.objects.filter(status='AVAILABLE').count()
    allocated_assets = Asset.objects.filter(status='ALLOCATED').count()
    pending_bookings = Booking.objects.filter(status='PENDING').count()
    maintenance_requests = MaintenanceRequest.objects.count()
    audits_count = Audit.objects.count()

    import json
    
    # Chart 1: Asset Category Distribution
    categories = AssetCategory.objects.all()
    category_names = json.dumps([c.name for c in categories])
    category_counts = json.dumps([Asset.objects.filter(category=c).count() for c in categories])

    # Chart 2: Asset Allocation Chart
    allocation_labels = json.dumps(['Available', 'Allocated', 'Maintenance', 'Inactive'])
    allocation_data = json.dumps([
        available_assets,
        allocated_assets,
        Asset.objects.filter(status='MAINTENANCE').count(),
        Asset.objects.filter(status='INACTIVE').count()
    ])

    # Chart 3: Maintenance Status
    maintenance_labels = json.dumps(['Open', 'In Progress', 'Resolved', 'Rejected'])
    maintenance_data = json.dumps([
        MaintenanceRequest.objects.filter(status='OPEN').count(),
        MaintenanceRequest.objects.filter(status='IN_PROGRESS').count(),
        MaintenanceRequest.objects.filter(status='RESOLVED').count(),
        MaintenanceRequest.objects.filter(status='REJECTED').count(),
    ])

    # Chart 4: Department Wise Assets
    departments = Department.objects.all()
    dept_names = json.dumps([d.department_name for d in departments])
    dept_assets = json.dumps([Asset.objects.filter(department=d).count() for d in departments])

    # Recent Activity
    recent_activities = ActivityLog.objects.all().order_by('-timestamp')[:5]

    context = {
        "user": user,
        "total_employees": total_employees,
        "total_departments": total_departments,
        "total_assets": total_assets,
        "available_assets": available_assets,
        "allocated_assets": allocated_assets,
        "pending_bookings": pending_bookings,
        "maintenance_requests": maintenance_requests,
        "audits_count": audits_count,
        "category_names": category_names,
        "category_counts": category_counts,
        "allocation_labels": allocation_labels,
        "allocation_data": allocation_data,
        "maintenance_labels": maintenance_labels,
        "maintenance_data": maintenance_data,
        "dept_names": dept_names,
        "dept_assets": dept_assets,
        "recent_activities": recent_activities,
    }

    return render(request, "AssetFlowApp/admin_dashboard.html", context)


def asset_manager_dashboard(request):
    if 'uid' not in request.session: return redirect("login")
    user = User.objects.get(id=request.session['uid'])
    
    total_assets = Asset.objects.count()
    available_assets = Asset.objects.filter(status='AVAILABLE').count()
    maintenance_requests = MaintenanceRequest.objects.filter(status__in=['OPEN', 'IN_PROGRESS']).count()
    pending_bookings = Booking.objects.filter(status='PENDING').count()
    recent_activities = ActivityLog.objects.filter(module__in=['Assets', 'Maintenance', 'Booking', 'Allocation']).order_by('-timestamp')[:5]
    
    context = {
        "user": user,
        "total_assets": total_assets,
        "available_assets": available_assets,
        "maintenance_requests": maintenance_requests,
        "pending_bookings": pending_bookings,
        "recent_activities": recent_activities,
    }
    return render(request, "AssetFlowApp/asset_manager_dashboard.html", context)


def department_head_dashboard(request):
    if 'uid' not in request.session: return redirect("login")
    user = User.objects.get(id=request.session['uid'])
    employee = Employee.objects.get(user=user)
    
    dept = employee.department
    dept_assets = Asset.objects.filter(department=dept).count() if dept else 0
    dept_employees = Employee.objects.filter(department=dept).count() if dept else 0
    recent_activities = ActivityLog.objects.all().order_by('-timestamp')[:5]
    
    context = {
        "user": user,
        "employee": employee,
        "dept_assets": dept_assets,
        "dept_employees": dept_employees,
        "recent_activities": recent_activities,
    }
    return render(request, "AssetFlowApp/department_head_dashboard.html", context)


def employee_dashboard(request):
    if 'uid' not in request.session: return redirect("login")
    user = User.objects.get(id=request.session['uid'])
    employee = Employee.objects.get(user=user)

    my_allocations = Allocation.objects.filter(employee=employee, status='ACTIVE')
    my_bookings = Booking.objects.filter(employee=employee).order_by('-created_at')[:5]
    my_maintenance = MaintenanceRequest.objects.filter(reported_by=employee).order_by('-created_at')[:5]

    context = {
        "user": user,
        "employee": employee,
        "my_allocations": my_allocations,
        "my_bookings": my_bookings,
        "my_maintenance": my_maintenance,
    }
    return render(request, "AssetFlowApp/employee_dashboard.html", context)

from django.contrib import messages

# --- DEPARTMENTS ---
def manage_departments(request):
    if 'uid' not in request.session: return redirect("login")
    user = User.objects.get(id=request.session['uid'])
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('department_name')
            status = request.POST.get('status') == 'True'
            if Department.objects.filter(department_name=name).exists():
                messages.error(request, "Department already exists!")
            else:
                Department.objects.create(department_name=name, status=status)
                ActivityLog.objects.create(user=user, action=f"Added Department: {name}", module="Organization")
                messages.success(request, "Department added successfully!")
        elif action == 'edit':
            dept_id = request.POST.get('department_id')
            name = request.POST.get('department_name')
            status = request.POST.get('status') == 'True'
            dept = Department.objects.get(id=dept_id)
            dept.department_name = name
            dept.status = status
            dept.save()
            ActivityLog.objects.create(user=user, action=f"Updated Department: {name}", module="Organization")
            messages.success(request, "Department updated successfully!")
        elif action == 'delete':
            dept_id = request.POST.get('department_id')
            dept = Department.objects.get(id=dept_id)
            if dept.employees.exists():
                messages.error(request, f"Cannot delete '{dept.department_name}' because it has active employees.")
            else:
                dept.delete()
                ActivityLog.objects.create(user=user, action=f"Deleted Department: {dept.department_name}", module="Organization")
                messages.success(request, "Department deleted successfully!")
        return redirect('manage_departments')
        
    departments = Department.objects.all()
    return render(request, "AssetFlowApp/organization/departments.html", {"user": user, "departments": departments})


# --- EMPLOYEES ---
def manage_employees(request):
    if 'uid' not in request.session: return redirect("login")
    user = User.objects.get(id=request.session['uid'])
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            email = request.POST.get('email')
            employee_code = request.POST.get('employee_code')
            if User.objects.filter(email=email).exists():
                messages.error(request, "User with this email already exists!")
                return redirect('manage_employees')
            if Employee.objects.filter(employee_code=employee_code).exists():
                messages.error(request, "Employee with this code already exists!")
                return redirect('manage_employees')
            
            new_user = User.objects.create(email=email, password=request.POST.get('password'), role=request.POST.get('role'))
            dept = Department.objects.get(id=request.POST.get('department'))
            Employee.objects.create(
                user=new_user, department=dept, employee_code=employee_code,
                first_name=request.POST.get('first_name'), last_name=request.POST.get('last_name'),
                contact_no=request.POST.get('contact_no')
            )
            ActivityLog.objects.create(user=user, action=f"Added Employee: {email}", module="Organization")
            messages.success(request, "Employee added successfully!")
            
        elif action == 'edit':
            emp_id = request.POST.get('employee_id')
            emp = Employee.objects.get(id=emp_id)
            emp.first_name = request.POST.get('first_name')
            emp.last_name = request.POST.get('last_name')
            emp.contact_no = request.POST.get('contact_no')
            emp.department = Department.objects.get(id=request.POST.get('department'))
            emp.save()
            
            emp.user.role = request.POST.get('role')
            emp.user.status = request.POST.get('status')
            emp.user.save()
            ActivityLog.objects.create(user=user, action=f"Updated Employee: {emp.user.email}", module="Organization")
            messages.success(request, "Employee updated successfully!")
            
        elif action == 'delete':
            emp_id = request.POST.get('employee_id')
            emp = Employee.objects.get(id=emp_id)
            if emp.allocations.filter(status='ACTIVE').exists():
                messages.error(request, "Cannot delete employee. They currently have active asset allocations.")
            else:
                emp.user.delete() # Deletes employee via cascade
                ActivityLog.objects.create(user=user, action=f"Deleted Employee: {emp.first_name}", module="Organization")
                messages.success(request, "Employee deleted successfully!")
        return redirect('manage_employees')
        
    employees = Employee.objects.all()
    departments = Department.objects.all()
    return render(request, "AssetFlowApp/organization/employees.html", {"user": user, "employees": employees, "departments": departments})

# --- ASSET CATEGORIES ---
def manage_categories(request):
    if 'uid' not in request.session: return redirect("login")
    user = User.objects.get(id=request.session['uid'])
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name')
            AssetCategory.objects.create(name=name, description=request.POST.get('description'))
            ActivityLog.objects.create(user=user, action=f"Added Category: {name}", module="Assets")
            messages.success(request, "Category added successfully!")
        elif action == 'edit':
            cat = AssetCategory.objects.get(id=request.POST.get('category_id'))
            cat.name = request.POST.get('name')
            cat.description = request.POST.get('description')
            cat.save()
            ActivityLog.objects.create(user=user, action=f"Updated Category: {cat.name}", module="Assets")
            messages.success(request, "Category updated successfully!")
        elif action == 'delete':
            AssetCategory.objects.get(id=request.POST.get('category_id')).delete()
            ActivityLog.objects.create(user=user, action="Deleted Category", module="Assets")
            messages.success(request, "Category deleted successfully!")
        return redirect('manage_categories')
        
    categories = AssetCategory.objects.all()
    return render(request, "AssetFlowApp/organization/categories.html", {"user": user, "categories": categories})

# --- ASSETS ---
def manage_assets(request):
    if 'uid' not in request.session: return redirect("login")
    user = User.objects.get(id=request.session['uid'])
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            import uuid
            qr_val = request.POST.get('qr_code')
            if not qr_val:
                qr_val = str(uuid.uuid4())[:8].upper()
            
            Asset.objects.create(
                asset_name=request.POST.get('asset_name'),
                category=AssetCategory.objects.get(id=request.POST.get('category')),
                department=Department.objects.get(id=request.POST.get('department')) if request.POST.get('department') else None,
                serial_number=request.POST.get('serial_number'),
                status=request.POST.get('status'),
                qr_code=qr_val,
                asset_image=request.FILES.get('asset_image')
            )
            ActivityLog.objects.create(user=user, action=f"Added Asset: {request.POST.get('asset_name')}", module="Assets")
            messages.success(request, "Asset added successfully!")
        elif action == 'edit':
            asset = Asset.objects.get(id=request.POST.get('asset_id'))
            asset.asset_name = request.POST.get('asset_name')
            asset.category = AssetCategory.objects.get(id=request.POST.get('category'))
            if request.POST.get('department'):
                asset.department = Department.objects.get(id=request.POST.get('department'))
            asset.serial_number = request.POST.get('serial_number')
            asset.status = request.POST.get('status')
            
            if request.FILES.get('asset_image'):
                asset.asset_image = request.FILES.get('asset_image')
                
            asset.save()
            ActivityLog.objects.create(user=user, action=f"Updated Asset: {asset.asset_name}", module="Assets")
            messages.success(request, "Asset updated successfully!")
        elif action == 'delete':
            Asset.objects.get(id=request.POST.get('asset_id')).delete()
            ActivityLog.objects.create(user=user, action="Deleted Asset", module="Assets")
            messages.success(request, "Asset deleted successfully!")
        return redirect('manage_assets')
        
    assets = Asset.objects.all()
    categories = AssetCategory.objects.all()
    departments = Department.objects.all()
    return render(request, "AssetFlowApp/assets/asset_list.html", {"user": user, "assets": assets, "categories": categories, "departments": departments})



from django.utils import timezone

# --- ALLOCATIONS ---
def allocate_asset(request):
    if 'uid' not in request.session: return redirect("login")
    user = User.objects.get(id=request.session['uid'])
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            asset = Asset.objects.get(id=request.POST.get('asset'))
            employee = Employee.objects.get(id=request.POST.get('employee'))
            if asset.status != 'AVAILABLE':
                messages.error(request, "Asset is not available for allocation.")
            else:
                Allocation.objects.create(asset=asset, employee=employee, allocated_by=user)
                asset.status = 'ALLOCATED'
                asset.save()
                ActivityLog.objects.create(user=user, action=f"Allocated Asset {asset.asset_name} to {employee.first_name}", module="Allocation")
                messages.success(request, "Asset allocated successfully!")
        elif action == 'return':
            alloc = Allocation.objects.get(id=request.POST.get('allocation_id'))
            alloc.status = 'RETURNED'
            alloc.return_date = timezone.now()
            alloc.save()
            alloc.asset.status = 'AVAILABLE'
            alloc.asset.save()
            ActivityLog.objects.create(user=user, action=f"Returned Asset {alloc.asset.asset_name}", module="Allocation")
            messages.success(request, "Asset returned successfully!")
        elif action == 'transfer':
            alloc = Allocation.objects.get(id=request.POST.get('allocation_id'))
            new_emp = Employee.objects.get(id=request.POST.get('new_employee'))
            
            # Close old allocation
            alloc.status = 'RETURNED'
            alloc.return_date = timezone.now()
            alloc.save()
            
            # Create new allocation
            Allocation.objects.create(asset=alloc.asset, employee=new_emp, allocated_by=user)
            ActivityLog.objects.create(user=user, action=f"Transferred Asset {alloc.asset.asset_name} to {new_emp.first_name}", module="Allocation")
            messages.success(request, "Asset transferred successfully!")
        return redirect('allocate_asset')
        
    allocations = Allocation.objects.all().order_by('-allocated_date')
    available_assets = Asset.objects.filter(status='AVAILABLE')
    employees = Employee.objects.all()
    return render(request, "AssetFlowApp/allocation/allocate_asset.html", {"user": user, "allocations": allocations, "available_assets": available_assets, "employees": employees})

# --- BOOKINGS ---
def manage_bookings(request):
    if 'uid' not in request.session: return redirect("login")
    user = User.objects.get(id=request.session['uid'])
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            asset_id = request.POST.get('asset')
            s_date = request.POST.get('start_date')
            e_date = request.POST.get('end_date')
            
            overlaps = Booking.objects.filter(
                asset_id=asset_id,
                status__in=['APPROVED', 'PENDING'],
                start_date__lte=e_date,
                end_date__gte=s_date
            )
            
            if overlaps.exists():
                messages.error(request, "Asset is already booked or pending for the selected dates.")
            else:
                Booking.objects.create(
                    asset=Asset.objects.get(id=asset_id),
                    employee=Employee.objects.get(id=request.POST.get('employee')),
                    start_date=s_date,
                    end_date=e_date
                )
                ActivityLog.objects.create(user=user, action=f"Created Booking Request", module="Booking")
                messages.success(request, "Booking requested successfully!")
        elif action == 'approve':
            b = Booking.objects.get(id=request.POST.get('booking_id'))
            b.status = 'APPROVED'
            b.save()
            messages.success(request, "Booking approved!")
        elif action == 'reject':
            b = Booking.objects.get(id=request.POST.get('booking_id'))
            b.status = 'REJECTED'
            b.save()
            messages.success(request, "Booking rejected!")
        return redirect('manage_bookings')
        
    bookings = Booking.objects.all().order_by('-created_at')
    assets = Asset.objects.all()
    employees = Employee.objects.all()
    return render(request, "AssetFlowApp/booking/create_booking.html", {"user": user, "bookings": bookings, "assets": assets, "employees": employees})

# --- MAINTENANCE ---
def manage_maintenance(request):
    if 'uid' not in request.session: return redirect("login")
    user = User.objects.get(id=request.session['uid'])
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            MaintenanceRequest.objects.create(
                asset=Asset.objects.get(id=request.POST.get('asset')),
                reported_by=Employee.objects.get(id=request.POST.get('employee')),
                issue_description=request.POST.get('description')
            )
            Asset.objects.filter(id=request.POST.get('asset')).update(status='MAINTENANCE')
            ActivityLog.objects.create(user=user, action=f"Maintenance Requested", module="Maintenance")
            messages.success(request, "Maintenance requested successfully!")
        elif action == 'resolve':
            m = MaintenanceRequest.objects.get(id=request.POST.get('request_id'))
            m.status = 'RESOLVED'
            m.resolved_by = user
            m.resolved_at = timezone.now()
            m.save()
            m.asset.status = 'AVAILABLE'
            m.asset.save()
            messages.success(request, "Maintenance resolved!")
        elif action == 'update_status':
            m = MaintenanceRequest.objects.get(id=request.POST.get('request_id'))
            new_status = request.POST.get('status')
            m.status = new_status
            if new_status in ['RESOLVED', 'REJECTED']:
                m.resolved_by = user
                m.resolved_at = timezone.now()
                if new_status == 'RESOLVED':
                    m.asset.status = 'AVAILABLE'
                elif new_status == 'REJECTED':
                    m.asset.status = 'AVAILABLE' # Assume it's available if request is rejected
                m.asset.save()
            m.save()
            messages.success(request, "Maintenance status updated!")
        return redirect('manage_maintenance')
        
    requests = MaintenanceRequest.objects.all().order_by('-created_at')
    assets = Asset.objects.all()
    employees = Employee.objects.all()
    return render(request, "AssetFlowApp/maintenance/maintenance_request.html", {"user": user, "requests": requests, "assets": assets, "employees": employees})

# --- AUDIT ---
def manage_audits(request):
    if 'uid' not in request.session: return redirect("login")
    user = User.objects.get(id=request.session['uid'])
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            Audit.objects.create(audit_name=request.POST.get('audit_name'), started_by=user)
            ActivityLog.objects.create(user=user, action=f"Started Audit", module="Audit")
            messages.success(request, "Audit started successfully!")
        elif action == 'complete':
            a = Audit.objects.get(id=request.POST.get('audit_id'))
            a.status = 'COMPLETED'
            a.end_date = timezone.now()
            a.save()
            messages.success(request, "Audit completed!")
        elif action == 'verify_asset':
            a = Audit.objects.get(id=request.POST.get('audit_id'))
            asset_id = request.POST.get('asset_id')
            if a.verified_assets:
                verified_list = a.verified_assets.split(',')
                if asset_id not in verified_list:
                    verified_list.append(asset_id)
                    a.verified_assets = ','.join(verified_list)
            else:
                a.verified_assets = str(asset_id)
            a.save()
            messages.success(request, f"Asset Verified in Audit: {a.audit_name}")
        return redirect('manage_audits')
        
    audits = Audit.objects.all().order_by('-start_date')
    
    # We will pass assets to the template for verification
    assets = Asset.objects.all()
    
    return render(request, "AssetFlowApp/audit/audit_cycle.html", {"user": user, "audits": audits, "assets": assets})

import csv
from django.http import HttpResponse

def export_audit_report(request, audit_id):
    if 'uid' not in request.session: return redirect("login")
    
    audit = Audit.objects.get(id=audit_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="audit_report_{audit.audit_name}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Audit Name', 'Started By', 'Start Date', 'End Date', 'Status'])
    writer.writerow([audit.audit_name, audit.started_by.email if audit.started_by else '', audit.start_date, audit.end_date, audit.status])
    writer.writerow([])
    writer.writerow(['Asset Name', 'Serial Number', 'Category', 'Verification Status'])
    
    all_assets = Asset.objects.all()
    verified_list = audit.verified_assets.split(',') if audit.verified_assets else []
    
    for asset in all_assets:
        status = 'Verified' if str(asset.id) in verified_list else 'Missing'
        writer.writerow([asset.asset_name, asset.serial_number, asset.category.name, status])
        
    return response

def export_assets(request):
    if 'uid' not in request.session: return redirect("login")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="assets_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Serial Number', 'Name', 'Category', 'Department', 'Status', 'Added On'])
    for a in Asset.objects.all():
        writer.writerow([a.serial_number, a.asset_name, a.category.name, a.department.department_name if a.department else '-', a.status, a.created_at])
    return response

def export_employees(request):
    if 'uid' not in request.session: return redirect("login")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Employee Code', 'Name', 'Email', 'Department', 'Role', 'Status'])
    for e in Employee.objects.all():
        writer.writerow([e.employee_code, f"{e.first_name} {e.last_name}", e.user.email, e.department.department_name if e.department else '-', e.user.role, e.user.status])
    return response
