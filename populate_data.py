import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentordesk.settings')
django.setup()

from academics.models import Class

classes = ['Class A', 'Class B', 'Class C', 'Class D', 'Class E', 'Class F', 'Class G']

for class_name in classes:
    cls, created = Class.objects.get_or_create(name=class_name)
    if created:
        print(f'Created {class_name}')
    else:
        print(f'{class_name} already exists')

print("Initial data population complete.")
