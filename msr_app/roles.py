# roles.py
from rolepermissions.roles import AbstractUserRole


class Manager(AbstractUserRole):
    available_permissions = {
        'manage_own_staff': True,  # Covers add/edit/delete staff under this manager
        'view_own_staff_reports': True,
        'change_own_staff_report_status': True,
    }

class Staff(AbstractUserRole):
    available_permissions = {
        'add_own_report': True,
        'edit_own_report': True,
        'delete_own_report': True,
        'view_own_info': True,
    }
