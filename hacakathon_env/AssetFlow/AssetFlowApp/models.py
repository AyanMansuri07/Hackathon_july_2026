from django.db import models


# ==========================
# User Model
# ==========================
class User(models.Model):

    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('ASSET_MANAGER', 'Asset Manager'),
        ('DEPARTMENT_HEAD', 'Department Head'),
        ('EMPLOYEE', 'Employee'),
    )

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    )

    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=30)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    otp = models.IntegerField(default=1234)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.email


# ==========================
# Department Model
# ==========================
class Department(models.Model):

    department_name = models.CharField(max_length=100, unique=True)

    parent_department = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_departments'
    )

    status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "department"

    def __str__(self):
        return self.department_name


# ==========================
# Employee Model
# ==========================
class Employee(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='employee_details'
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )

    employee_code = models.CharField(max_length=20, unique=True)

    first_name = models.CharField(max_length=30)

    last_name = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    contact_no = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    profile_pic = models.FileField(
        upload_to='profile/',
        default='profile/default.png',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "employee"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
# ==========================
# Asset Category Model
# ==========================
class AssetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "asset_category"

    def __str__(self):
        return self.name

# ==========================
# Asset Model
# ==========================
class Asset(models.Model):
    STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('ALLOCATED', 'Allocated'),
        ('MAINTENANCE', 'Maintenance'),
        ('INACTIVE', 'Inactive'),
    )
    asset_name = models.CharField(max_length=100)
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE, related_name='assets')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='department_assets')
    serial_number = models.CharField(max_length=100, unique=True)
    qr_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    asset_image = models.FileField(upload_to='assets/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "asset"

    def __str__(self):
        return f"{self.asset_name} ({self.serial_number})"

# ==========================
# Allocation Model
# ==========================
class Allocation(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='allocations')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='allocations')
    allocated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    allocated_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=(('ACTIVE', 'Active'), ('RETURNED', 'Returned')), default='ACTIVE')

    class Meta:
        db_table = "allocation"

# ==========================
# Booking Model
# ==========================
class Booking(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='bookings')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=(('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')), default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "booking"

# ==========================
# Maintenance Request Model
# ==========================
class MaintenanceRequest(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_requests')
    reported_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reported_issues')
    issue_description = models.TextField()
    status = models.CharField(max_length=20, choices=(('OPEN', 'Open'), ('IN_PROGRESS', 'In Progress'), ('RESOLVED', 'Resolved'), ('REJECTED', 'Rejected')), default='OPEN')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_issues')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "maintenance_request"

# ==========================
# Audit Model
# ==========================
class Audit(models.Model):
    audit_name = models.CharField(max_length=100)
    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='started_audits')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=(('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed')), default='IN_PROGRESS')

    class Meta:
        db_table = "audit"

# ==========================
# Activity Log Model
# ==========================
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=200)
    module = models.CharField(max_length=50) # e.g. 'Assets', 'Employees', 'Audits'
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activity_log"
