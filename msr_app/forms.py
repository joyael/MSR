# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser , Report
from msr_app import roles
from rolepermissions.roles import assign_role

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'address', 'phone_number', 'role', 'password1', 'password2')  

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True  # Needed to allow login to admin
        if commit:
            user.save()  # Now the user has an ID and can have m2m relations
            # Assign role-based permissions using django-role-permissions
            if user.role == 'manager':
                assign_manager_permissions(user)
                assign_role(user, 'manager')
            elif user.role == 'staff':
                assign_manager_permissions(user)
                assign_role(user, 'staff')
        return user

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

def assign_manager_permissions(user):
    content_types = ContentType.objects.get_for_models(CustomUser, Report)
    perms = Permission.objects.filter(content_type__in=content_types.values(), codename__in=[
        'view_customuser', 'change_customuser',
        'view_report', 'change_report',
    ])
    user.user_permissions.set(perms)

def assign_staff_permissions(user):
    content_types = ContentType.objects.get_for_models(CustomUser, Report)
    perms = Permission.objects.filter(content_type__in=content_types.values(), codename__in=[
        'view_customuser', 'change_customuser',
        'view_report', 'change_report',
    ])
    user.user_permissions.set(perms)