from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from .managers import CustomUserManager
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
# Create your models here.


STATUS_CHOICES = [
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Others', 'Others'),
]

class CustomManager(models.Manager):
    def get_queryset(self):
        return super(__class__, self).get_queryset().filter(is_deleted=False)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """ Custom User Model """

    full_name = models.CharField(max_length=100, blank=True, null=True)
    email= models.EmailField(max_length=100, unique=True)
    gender = models.CharField(max_length=10, blank=True, null=True, choices=GENDER_CHOICES)
    phone_regex = RegexValidator(regex=r'^\d{10}$', message="Phone number must be 10 digits.")
    phone = models.CharField(validators=[phone_regex], max_length=10, unique=True)

    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.full_name


class BaseAbstractStructure(models.Model):
    is_deleted = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='+')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    cmobjects = CustomManager()

    class Meta:
        abstract = True


class OTP(models.Model):
    """Model to store OTPs for user verification."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        """Check if the OTP is still valid."""
        return timezone.now() < self.expires_at


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
