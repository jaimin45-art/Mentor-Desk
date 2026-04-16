import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentordesk.settings')
django.setup()

from academics.models import Class, StudentProfile, MentorProfile, ParentProfile, FacultyProfile

print("=== Classes in DB ===")
classes = list(Class.objects.all())
if classes:
    for c in classes:
        print(f"  id={c.id} | name={c.name}")
else:
    print("  *** NO CLASSES FOUND! This is the problem. ***")
    print("  Creating Class A, B, C ...")
    Class.objects.get_or_create(name='Class A')
    Class.objects.get_or_create(name='Class B')
    Class.objects.get_or_create(name='Class C')
    print("  ✅ Classes created!")

print("\n=== StudentProfiles ===", StudentProfile.objects.count())
print("=== MentorProfiles ===", MentorProfile.objects.count())
print("=== FacultyProfiles ===", FacultyProfile.objects.count())
print("=== ParentProfiles ===", ParentProfile.objects.count())
