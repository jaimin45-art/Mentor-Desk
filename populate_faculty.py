import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentordesk.settings')
django.setup()

from core.pre_auth_models import PreAuthorizedData
from django.db import transaction

faculty_emails = [
    'faculty3@example.com',
    'faculty4@example.com',
    'faculty5@example.com',
]

print("Pre-authorizing faculty 3, 4, 5...")

with transaction.atomic():
    for email in faculty_emails:
        # Create PreAuthorizedData entry
        pre_auth, created = PreAuthorizedData.objects.get_or_create(
            email=email,
            defaults={'role': 'FACULTY'}
        )
        if created:
            print(f"Pre-authorized: {email}")
        else:
            print(f"Already pre-authorized: {email}")

print("Pre-authorization complete. Faculty can now register using their emails.")
