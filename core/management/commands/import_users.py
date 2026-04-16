import openpyxl
from django.core.management.base import BaseCommand
from core.models import PreAuthorizedData
from academics.models import Class

class Command(BaseCommand):
    help = 'Imports user data from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to the Excel file')

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        
        try:
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            
            # Assuming headers: Email, Role, Class, RollNumber
            # Skip header row
            count = 0
            for row in sheet.iter_rows(min_row=2, values_only=True):
                email, role, class_name, roll_number = row
                
                if not email:
                    continue
                    
                role = role.upper().strip() if role else ''
                if role not in ['STUDENT', 'MENTOR', 'FACULTY']:
                    self.stdout.write(self.style.WARNING(f"Invalid role for {email}: {role}"))
                    continue
                
                # Create or Update
                obj, created = PreAuthorizedData.objects.update_or_create(
                    email=email,
                    defaults={
                        'role': role,
                        'assigned_class_name': class_name,
                        'roll_number': roll_number
                    }
                )
                
                # Ensure Class exists if provided
                if class_name:
                    Class.objects.get_or_create(name=class_name)
                    
                count += 1
                
            self.stdout.write(self.style.SUCCESS(f'Successfully imported/updated {count} users.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}'))
