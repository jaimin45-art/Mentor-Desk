from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models import User
from academics.models import StudentProfile, Class

class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    roll_number = forms.CharField(max_length=20, required=True)
    parent_email = forms.EmailField(required=True)
    assigned_class = forms.ModelChoiceField(queryset=Class.objects.all(), required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                roll_number=self.cleaned_data['roll_number'],
                parent_email=self.cleaned_data['parent_email'],
                assigned_class=self.cleaned_data['assigned_class']
            )
        return user

class MentorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_mentor = True
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # MentorProfile logic if any additional fields needed
            from academics.models import MentorProfile
            MentorProfile.objects.create(user=user)
        return user

class FacultyRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

from .pre_auth_models import PreAuthorizedData

class UnifiedRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    semester = forms.IntegerField(min_value=1, max_value=8, required=False, help_text="Required for Students and Mentors (1-8)")
    roll_number = forms.CharField(max_length=20, required=False, help_text="Note: Enrollment numbers are for Students and Parents.")
    assigned_class = forms.ModelChoiceField(queryset=Class.objects.all(), required=False, help_text="Required for Students and Mentors")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not PreAuthorizedData.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is not pre-authorized. Please contact the administrator.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if email:
            pre_auth = PreAuthorizedData.objects.filter(email=email).first()
            if pre_auth:
                if pre_auth.role == 'STUDENT':
                    if not cleaned_data.get('roll_number'):
                        self.add_error('roll_number', 'Enrollment Number is required for students.')
                    if not cleaned_data.get('assigned_class'):
                        self.add_error('assigned_class', 'Class is required for students.')
                elif pre_auth.role == 'MENTOR':
                    if not cleaned_data.get('assigned_class'):
                        self.add_error('assigned_class', 'Class assignment is required for mentors.')
                elif pre_auth.role == 'PARENT':
                    if not cleaned_data.get('roll_number'):
                        self.add_error('roll_number', 'The Enrollment Number of your child is required.')
                    else:
                        from academics.models import StudentProfile
                        if not StudentProfile.objects.filter(roll_number=cleaned_data.get('roll_number')).exists():
                            self.add_error('roll_number', 'No student found with this Enrollment Number.')
        return cleaned_data

    def save(self, commit=True):
        from django.db import transaction
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        user.email = email
        
        # Auto-assign role based on PreAuthorizedData
        pre_auth = PreAuthorizedData.objects.get(email=email)
        
        if pre_auth.role == 'STUDENT':
            user.is_student = True
        elif pre_auth.role == 'MENTOR':
            user.is_mentor = True
        elif pre_auth.role == 'FACULTY':
            user.is_faculty = True
        elif pre_auth.role == 'PARENT':
            user.is_parent = True
            
        if commit:
            with transaction.atomic():
                user.save()
                
                # Create profiles and assign class
                assigned_class = self.cleaned_data.get('assigned_class')
                
                # Fallback to pre-auth class if not provided by form
                if not assigned_class and pre_auth.assigned_class_name:
                    assigned_class = Class.objects.filter(name=pre_auth.assigned_class_name).first()

                if user.is_student:
                    roll_number = self.cleaned_data.get('roll_number') or pre_auth.roll_number or 'TEMP'
                    StudentProfile.objects.create(
                        user=user,
                        roll_number=roll_number,
                        parent_email=f"parent.{user.username}@example.com",
                        assigned_class=assigned_class,
                        semester=self.cleaned_data.get('semester') or 1
                    )
                elif user.is_mentor:
                    from academics.models import MentorProfile
                    MentorProfile.objects.create(
                        user=user,
                        semester=self.cleaned_data.get('semester') or 1
                    )
                    if assigned_class:
                        assigned_class.mentors.add(user)
                elif user.is_faculty:
                    from academics.models import FacultyProfile
                    FacultyProfile.objects.create(user=user)
                elif user.is_parent:
                    from academics.models import ParentProfile
                    student = StudentProfile.objects.filter(roll_number=self.cleaned_data.get('roll_number')).first()
                    ParentProfile.objects.create(user=user, student=student)
                
        return user
