from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser , Report
from .forms import CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role','is_active')
    list_filter = ('is_active', 'role')
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': (
                'address',
                'phone_number',
                'role',
                'manager',
            ),
        }),
    )
    add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': (
            'username',
            'first_name',
            'last_name',
            'email',
            'address',
            'phone_number',
            'role',
            'manager',
            'password1',
            'password2',
        ),
    }),
    )
  
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superuser sees all users
        if request.user.role == 'manager':
            return qs.filter(manager=request.user)
        return qs

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True  # Superuser can change any object
        elif request.user.role == 'manager' and obj:
            return obj.manager == request.user
        elif request.user.role == 'staff' and obj:
            return obj == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True  # Superuser can delete any object
        # if request.user.role == 'manager' and obj:
        #     return obj.manager == request.user
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True  # Superuser can add any object
        return request.user.role in ['admin', 'manager']

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            super().save_model(request, obj, form, change)
            return
        if request.user.role == 'manager':
            obj.manager = request.user  # Auto-assign manager
            obj.role = 'staff'  # Enforce staff role
        super().save_model(request, obj, form, change)

class ReportAdmin(admin.ModelAdmin):
    model = Report
    list_display = ['report_name', 'staff', 'status']
    # readonly_fields = ['report_name', 'project_name', 'address', 'phone_number', 'id_proof', 'comment', 'date', 'staff']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superuser sees all reports
        
        if request.user.role == 'staff':
            return qs.filter(staff=request.user)
        elif request.user.role == 'manager':
            return qs.filter(staff__manager=request.user)
        
        return qs

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True  # Superuser can change any object
        
        if request.user.role == 'staff':
            return obj is None or obj.staff == request.user
        elif request.user.role == 'manager':
            return obj is None or (obj.staff and obj.staff.manager == request.user)
        
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True  # Superuser can delete any object
        
        if request.user.role == 'staff':
            return obj is None or obj.staff == request.user
        elif request.user.role == 'manager':
            return False  # Managers can't delete reports
        
        return True

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            super().save_model(request, obj, form, change)
            return
        
        if request.user.role == 'staff' and not change:
            obj.staff = request.user  # Auto-assign
        elif request.user.role == 'manager':
            if 'status' in form.changed_data:
                pass  # Only allow status to be changed
            else:
                return  # Prevent other changes
        
        super().save_model(request, obj, form, change)

# Unregister the default User admin if necessary
try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass  # Ignore if not registered
# Register the custom User admin
admin.site.register(CustomUser , CustomUserAdmin)
# Register the Report model
admin.site.register(Report, ReportAdmin)