from django.db import models
from django.conf import settings

class PreAuthorizedData(models.Model):
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('MENTOR', 'Mentor'),
        ('FACULTY', 'Faculty'),
        ('PARENT', 'Parent'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    # Storing class name as string to avoid strict FK constraints during import if class doesn't exist yet,
    # or better, use FK but handle creation. Let's use string for robust import, then link.
    # Actually, FK is better for integrity. We'll ensure Classes exist.
    assigned_class_name = models.CharField(max_length=50, blank=True, null=True) 
    roll_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.email} ({self.role})"
