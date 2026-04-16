import openpyxl
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "Users"

# Headers
ws.append(["Email", "Role", "Class", "RollNumber"])

# Data
data = [
    ["student1@example.com", "STUDENT", "Class A", "A101"],
    ["student2@example.com", "STUDENT", "Class B", "B101"],
    ["student3@example.com", "STUDENT", "Class A", "A102"],
    ["student4@example.com", "STUDENT", "Class C", "C101"],
    ["student5@example.com", "STUDENT", "Class C", "C102"],
    ["student_sem2@example.com", "STUDENT", "Class A", "A103"], # For testing Semester 2
    
    ["mentor1@example.com", "MENTOR", "Class A", ""],
    ["mentor2@example.com", "MENTOR", "Class B", ""],
    ["mentor3@example.com", "MENTOR", "Class C", ""],
    
    ["faculty1@example.com", "FACULTY", "", ""],
    ["faculty2@example.com", "FACULTY", "", ""],
]

for row in data:
    ws.append(row)

wb.save("users_data.xlsx")
print("Sample Excel file 'users_data.xlsx' created.")
