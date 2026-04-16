import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentordesk.settings')
django.setup()

from core.pre_auth_models import PreAuthorizedData
from django.db import transaction

parent_emails = [
    'parent1@example.com',
    'parent2@example.com',
    'parent3@example.com',
]

print("Pre-authorizing parents 1 and 2...")

with transaction.atomic():
    for email in parent_emails:
        # Create PreAuthorizedData entry
        pre_auth, created = PreAuthorizedData.objects.get_or_create(
            email=email,
            defaults={'role': 'PARENT'}
        )
        if created:
            print(f"Pre-authorized parent: {email}")
        else:
            print(f"Already pre-authorized: {email}")

print("Pre-authorization complete. Parents can now register using their emails.")
