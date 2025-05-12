from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser , Report
from .forms import CustomUserCreationForm
from django.db.models import Q
import datetime

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role', 'is_active')
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
    ordering = ('role','username')


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "manager":
            # Filter the queryset to only include users with the role of 'manager'
            kwargs["queryset"] = CustomUser.objects.filter(role='manager')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.role == 'manager':
            return qs.filter(Q(manager=request.user) | Q(id=request.user.id))
        if request.user.role == 'staff':
            return qs.filter(id=request.user.id)
        return qs

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True  
        if obj is None:
            return True
        elif request.user.role == 'manager':
            return obj.manager == request.user or obj.id == request.user.id
        elif request.user.role == 'staff' and obj:
            return obj == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True  
        if obj is None:
            return True
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True  # Superuser can add any object

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            super().save_model(request, obj, form, change)
            return
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if request.user.role == 'staff':
            readonly_fields = ['manager', 'role']
        elif request.user.role == 'manager':
            readonly_fields = ['manager', 'role']
        return readonly_fields
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        user_queryset = self.get_queryset(request)
        total_manager_count = user_queryset.filter(role='manager').count()
        total_staff_count = user_queryset.filter(role='staff').count()
        extra_context['total_manager_count'] = total_manager_count
        extra_context['total_staff_count'] = total_staff_count
        return super().changelist_view(request, extra_context=extra_context)

    def has_module_permission(self, request):
        return request.user.is_authenticated

class ReportAdmin(admin.ModelAdmin):
    model = Report
    list_display = ['report_name', 'project_name', 'staff', 'status']
    list_filter = ('status', 'project_name')
    

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  #Superuser sees all reports
        if request.user.role == 'staff':
            return qs.filter(staff=request.user)
        elif request.user.role == 'manager':
            return qs.filter(staff__manager=request.user)
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "staff":
            # Filter the queryset to only include users with the role of 'manager'
            kwargs["queryset"] = CustomUser.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True  # Superuser can change any object
        if obj is None:
            return True
        if request.user.role == 'staff':
            return obj is None or obj.staff == request.user
        elif request.user.role == 'manager':
            return obj is None or (obj.staff and obj.staff.manager == request.user)
        return True
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if request.user.role == 'staff':
            readonly_fields = ['status', 'date', 'approved_date']
        elif request.user.role == 'manager':
            readonly_fields = [
                'report_name', 'project_name', 'address', 'phone_number',
                'id_proof', 'date', 'staff', 'approved_date'
            ]
        elif request.user.is_superuser:
            readonly_fields = [
                'report_name', 'project_name', 'address', 'phone_number',
                'id_proof', 'date', 'staff', 'approved_date','status'
            ]
        return readonly_fields
    
    def has_add_permission(self, request):
        if request.user.role == 'staff':
            return True 
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
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
            obj.staff = request.user
        if change:
            original = Report.objects.get(pk=obj.pk)
            original_sts_value = getattr(original, 'status')
            new_ts_value = getattr(obj, 'status')
            if original_sts_value!='approved' and new_ts_value == 'approved':
                obj.approved_date = datetime.date.today()
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        user_queryset = self.get_queryset(request)
        approved_count = user_queryset.filter(status='approved').count()
        rejected_count = user_queryset.filter(status='rejected').count()
        pending_count = user_queryset.filter(status='pending').count()
        extra_context['approved_count'] = approved_count
        extra_context['rejected_count'] = rejected_count
        extra_context['pending_count'] = pending_count
        return super().changelist_view(request, extra_context=extra_context)
    
    def has_module_permission(self, request):
        return request.user.is_authenticated

# Unregister the default User admin if necessary
try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass  #Ignore if not registered
# Register the custom User admin
admin.site.register(CustomUser , CustomUserAdmin)
# Register the Report model
admin.site.register(Report, ReportAdmin)