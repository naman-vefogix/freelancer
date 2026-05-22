from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {'fields' : ('role', 'is_verified')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields' : ('role', 'isVerified' )}),
    )
    list_display = ('username', 'email', 'role', 'is_verified')
    list_filter = ('role', 'is_verified')
