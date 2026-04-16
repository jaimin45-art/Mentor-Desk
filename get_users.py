import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentordesk.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

print("--- User Accounts ---")
for u in User.objects.all():
    role = 'Student' if getattr(u, 'is_student', False) else 'Mentor' if getattr(u, 'is_mentor', False) else 'Faculty' if getattr(u, 'is_faculty', False) else 'Other/Admin'
    enrollment = ""
    if role == 'Student' and hasattr(u, 'student_profile'):
        enrollment = u.student_profile.roll_number
    print(f"Username: {u.username} | Email: {u.email} | Role: {role} | Enrollment/Roll: {enrollment}")

print("\n--- Pre-Authorized Data (for Registration) ---")
from core.pre_auth_models import PreAuthorizedData
for pd in PreAuthorizedData.objects.all():
    print(f"Email: {pd.email} | Role: {pd.role} | Roll No: {pd.roll_number} | Class: {pd.assigned_class_name}")
