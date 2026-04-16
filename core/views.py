from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import TemplateView, CreateView
from .forms import StudentRegistrationForm, MentorRegistrationForm, FacultyRegistrationForm, UnifiedRegistrationForm
from .models import User

def register(request):
    # return render(request, 'core/register_landing.html')
    # Redirecting to unified registration directly for Excel automation flow
    return redirect('unified_register')

class UnifiedRegisterView(CreateView):
    model = User
    form_class = UnifiedRegistrationForm
    template_name = 'core/register_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'User'
        return context

    def form_valid(self, form):
        try:
            user = form.save()
        except Exception as e:
            from django.contrib import messages
            messages.error(self.request, f"Registration failed: {e}. Please try again.")
            return self.form_invalid(form)
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        # Redirect to specific dashboard based on role
        if user.is_student:
             return redirect('student_dashboard')
        elif user.is_mentor:
             return redirect('mentor_dashboard')
        elif user.is_faculty:
             return redirect('faculty_dashboard')
        elif user.is_parent:
             return redirect('parent_dashboard')
        return redirect('dashboard')

class StudentRegisterView(CreateView):
    model = User
    form_class = StudentRegistrationForm
    template_name = 'core/register_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Student'
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('dashboard')

class MentorRegisterView(CreateView):
    model = User
    form_class = MentorRegistrationForm
    template_name = 'core/register_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Mentor'
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('dashboard')

class FacultyRegisterView(CreateView):
    model = User
    form_class = FacultyRegistrationForm
    template_name = 'core/register_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Faculty'
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('dashboard')

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')
