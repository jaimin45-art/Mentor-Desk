import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentordesk.settings')
django.setup()

from core.pre_auth_models import PreAuthorizedData
from core.models import User

print("=== PreAuthorizedData entries ===")
for p in PreAuthorizedData.objects.all():
    print(f"  {p.email} | role={p.role} | class={p.assigned_class_name} | roll={p.roll_number}")

print("\n=== Current non-superuser Users ===")
for u in User.objects.filter(is_superuser=False):
    print(f"  {u.username} | {u.email} | student={u.is_student} | mentor={u.is_mentor} | parent={u.is_parent} | faculty={u.is_faculty}")
