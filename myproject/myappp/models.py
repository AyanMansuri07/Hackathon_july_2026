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
    

from django.db import models

class AssetCategory(models.Model):

    category_name = models.CharField(max_length=100, unique=True)

    description = models.TextField(blank=True, null=True)

    no_of_asset = models.IntegerField(default=0)

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name
    

class Asset(models.Model):

    asset_name = models.CharField(
        max_length=100
    )


    asset_code = models.CharField(
        max_length=50,
        unique=True
    )


    category = models.ForeignKey(
    AssetCategory,
    on_delete=models.CASCADE,
    related_name="assets"
    )

    brand = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )


    model_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )


    serial_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )


    purchase_date = models.DateField(
        blank=True,
        null=True
    )


    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )


    warranty_expiry = models.DateField(
        blank=True,
        null=True
    )


    STATUS_CHOICES = (

        ('AVAILABLE','Available'),

        ('ALLOCATED','Allocated'),

        ('MAINTENANCE','Maintenance'),

        ('DAMAGED','Damaged'),

        ('SCRAPPED','Scrapped'),

    )


    asset_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="AVAILABLE"
    )


    CONDITION_CHOICES = (

        ('NEW','New'),

        ('GOOD','Good'),

        ('USED','Used'),

        ('DAMAGED','Damaged'),

    )


    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default="NEW"
    )


    location = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )


    description = models.TextField(
        blank=True,
        null=True
    )




    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):

        return self.asset_name
    

class AssetAllocation(models.Model):

    asset = models.ForeignKey(
    Asset,
    on_delete=models.CASCADE,
    related_name="allocations"
    )


    employee = models.ForeignKey(
    Employee,
    on_delete=models.CASCADE,
    related_name="allocated_assets"
    )


    allocated_by = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="asset_allocations"
    )

    allocation_date = models.DateTimeField(
        auto_now_add=True
    )


    return_date = models.DateTimeField(
        blank=True,
        null=True
    )


    STATUS_CHOICES = (

        ('ALLOCATED','Allocated'),

        ('RETURNED','Returned'),

        ('PENDING','Pending'),

    )


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ALLOCATED"
    )


    remarks = models.TextField(
        blank=True,
        null=True
    )


    def __str__(self):

        return self.asset.asset_name
    
class AssetRequest(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="asset_requests"
    )

    asset_name = models.CharField(
        max_length=100
    )

    reason = models.TextField()


    STATUS = (

        ("PENDING","Pending"),

        ("APPROVED","Approved"),

        ("REJECTED","Rejected"),

    )


    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="PENDING"
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.asset_name