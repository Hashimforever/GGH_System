from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    filter_horizontal = ('permissions',)


class CustomUserAdmin(UserAdmin):
    # Add 'roles' to the fieldsets so they can be assigned in the Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Roles', {'fields': ('roles',)}),
    )
    filter_horizontal = UserAdmin.filter_horizontal + ('roles',)

# Unregister if previously registered dynamically, then register with CustomUserAdmin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
