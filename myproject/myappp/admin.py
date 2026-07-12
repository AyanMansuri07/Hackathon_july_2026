from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Employee)
admin.site.register(Department)
admin.site.register(AssetCategory)
admin.site.register(Asset)
admin.site.register(AssetAllocation)