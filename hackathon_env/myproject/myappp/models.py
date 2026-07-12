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