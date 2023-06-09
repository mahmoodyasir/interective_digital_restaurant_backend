from django.contrib import admin
from .models import *

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['id', 'prouser', 'image', 'profileImageUrl']
    list_per_page = 10


class UserAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['id', 'email', 'is_staff']
    list_per_page = 10


admin.site.register(Profile, ProfileAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(AdminUserInfo)

