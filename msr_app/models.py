from django.contrib.auth.models import AbstractUser , Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    manager = models.ForeignKey('self', related_name='staff_members', null=True, blank=True, on_delete=models.SET_NULL)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set', 
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    REQUIRED_FIELDS = ['first_name', 'last_name']

class Report(models.Model):
    report_name = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    id_proof = models.ImageField(upload_to='id_proofs/')
    comment = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    staff = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)
    approved_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.report_name

