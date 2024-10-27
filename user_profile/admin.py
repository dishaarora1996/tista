from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, OTP

class CustomUserAdmin(BaseUserAdmin):
    """Admin view for CustomUser with fields for phone login."""
    list_display = ('full_name', 'email', 'phone', 'is_active', 'is_verified', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_verified', 'is_staff')
    search_fields = ('email', 'phone', 'full_name')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'email', 'gender')}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2', 'full_name', 'email', 'is_active', 'is_verified')}
        ),
    )

class OTPAdmin(admin.ModelAdmin):
    """Admin view for OTP with user and expiration info."""
    list_display = ('user', 'otp_code', 'created_at', 'expires_at')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('user__phone', 'otp_code')

# Register the models with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OTP, OTPAdmin)
