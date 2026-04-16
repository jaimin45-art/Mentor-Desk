from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from .models import Class, Subject, Attendance, LeaveApplication, Achievement, StudentProfile, Notification
from core.models import User
import datetime

class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.is_student:
            return redirect('student_dashboard')
        elif request.user.is_mentor:
            return redirect('mentor_dashboard')
        elif request.user.is_faculty:
            return redirect('faculty_dashboard')
        elif getattr(request.user, 'is_parent', False):
            return redirect('parent_dashboard')
        return redirect('admin:index')

class StudentDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'academics/dashboard_student.html'

    def test_func(self):
        return self.request.user.is_student

    def get(self, request, *args, **kwargs):
        try:
            _ = request.user.student_profile
        except Exception:
            from django.contrib import messages
            from django.contrib.auth import logout
            logout(request)
            messages.error(request, "Your student profile is incomplete. Please re-register or contact the administrator.")
            return redirect('login')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user
        profile = student.student_profile
        
        # Filter subjects by semester
        semester_subjects = Subject.objects.filter(assigned_class=profile.assigned_class, semester=profile.semester)
        
        context['attendance_total'] = Attendance.objects.filter(student=student, subject__in=semester_subjects).count()
        context['attendance_present'] = Attendance.objects.filter(student=student, status='PRESENT', subject__in=semester_subjects).count()
        if context['attendance_total'] > 0:
            context['attendance_percentage'] = (context['attendance_present'] / context['attendance_total']) * 100
        else:
            context['attendance_percentage'] = 0
            
        context['leaves_pending'] = LeaveApplication.objects.filter(student=student, status='PENDING').count()
        context['recent_attendance'] = Attendance.objects.filter(student=student, subject__in=semester_subjects).order_by('-date')[:5]
        
        # Leaves & Achievements History
        context['recent_leaves'] = LeaveApplication.objects.filter(student=student).order_by('-applied_on')[:5]
        context['recent_achievements'] = Achievement.objects.filter(student=student).order_by('-submitted_on')[:5]
        
        # Notifications
        context['notifications'] = Notification.objects.filter(recipient=student).order_by('-created_at')[:5]
        return context

class MentorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'academics/dashboard_mentor.html'

    def test_func(self):
        return self.request.user.is_mentor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mentor = self.request.user
        classes = Class.objects.filter(mentors=mentor)
        context['classes'] = classes
        context['pending_leaves'] = LeaveApplication.objects.filter(
            student__student_profile__assigned_class__in=classes,
            status='PENDING'
        ).distinct()
        
        # Get students for each class
        class_students = {}
        for cls in classes:
            students_with_attendance = []
            students = StudentProfile.objects.filter(assigned_class=cls)
            for student_profile in students:
                total = Attendance.objects.filter(student=student_profile.user).count()
                present = Attendance.objects.filter(student=student_profile.user, status='PRESENT').count()
                attendance_percentage = (present / total * 100) if total > 0 else 0
                # Subject-wise breakdown
                subjects = Subject.objects.filter(assigned_class=cls, semester=student_profile.semester)
                subject_breakdown = []
                for subject in subjects:
                    sub_total = Attendance.objects.filter(student=student_profile.user, subject=subject).count()
                    if sub_total > 0:
                        sub_present = Attendance.objects.filter(student=student_profile.user, subject=subject, status='PRESENT').count()
                        sub_absent = sub_total - sub_present
                        subject_breakdown.append({
                            'name': subject.name,
                            'present': sub_present,
                            'absent': sub_absent,
                        })

                students_with_attendance.append({
                    'profile': student_profile,
                    'attendance_percentage': attendance_percentage,
                    'subject_breakdown': subject_breakdown
                })
            class_students[cls] = students_with_attendance
        context['class_students'] = class_students
        
        return context

class FacultyDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'academics/dashboard_faculty.html'

    def test_func(self):
        return self.request.user.is_faculty

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = self.request.user
        context['subjects'] = Subject.objects.filter(faculty=faculty)
        return context

class ParentDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'academics/dashboard_parent.html'

    def test_func(self):
        return getattr(self.request.user, 'is_parent', False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent = self.request.user
        try:
            student = parent.parent_profile.student.user
            profile = student.student_profile
            
            context['student'] = student
            context['student_profile'] = profile
            
            semester_subjects = Subject.objects.filter(assigned_class=profile.assigned_class, semester=profile.semester)
            
            # Attendance
            context['attendance_total'] = Attendance.objects.filter(student=student, subject__in=semester_subjects).count()
            context['attendance_present'] = Attendance.objects.filter(student=student, status='PRESENT', subject__in=semester_subjects).count()
            if context['attendance_total'] > 0:
                context['attendance_percentage'] = (context['attendance_present'] / context['attendance_total']) * 100
            else:
                context['attendance_percentage'] = 0
            
            context['recent_attendance'] = Attendance.objects.filter(student=student, subject__in=semester_subjects).order_by('-date')[:10]
            
            # Achievements (Results)
            context['recent_achievements'] = Achievement.objects.filter(student=student).order_by('-submitted_on')[:10]
            
            # Mentors and their Phone Numbers
            if profile.assigned_class:
                context['mentors'] = profile.assigned_class.mentors.all()
            else:
                context['mentors'] = []
                
        except (AttributeError, Exception):
            context['student'] = None
            
        return context

class LeaveCreateView(LoginRequiredMixin, CreateView):
    model = LeaveApplication
    fields = ['reason', 'image_proof']
    template_name = 'academics/leave_form.html'
    success_url = reverse_lazy('student_dashboard')

    def form_valid(self, form):
        form.instance.student = self.request.user
        messages.success(self.request, "Leave application submitted successfully.")
        return super().form_valid(form)

class LeaveApprovalView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_mentor or self.request.user.is_faculty

    def post(self, request, pk):
        leave = get_object_or_404(LeaveApplication, pk=pk)
        action = request.POST.get('action')
        if action == 'approve':
            leave.status = 'APPROVED'
            messages.success(request, "Leave approved.")
        elif action == 'reject':
            leave.status = 'REJECTED'
            messages.success(request, "Leave rejected.")
        leave.reviewed_by = request.user
        leave.save()
        return redirect('dashboard')

class MarkAttendanceView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_faculty

    def get(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id, faculty=request.user)
        students = StudentProfile.objects.filter(assigned_class=subject.assigned_class)
        return render(request, 'academics/mark_attendance.html', {'subject': subject, 'students': students, 'date': datetime.date.today()})

    def post(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id, faculty=request.user)
        date_str = request.POST.get('date')
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        
        students = StudentProfile.objects.filter(assigned_class=subject.assigned_class)
        for student_profile in students:
            status = request.POST.get(f'student_{student_profile.user.id}')
            if status:
                Attendance.objects.update_or_create(
                    student=student_profile.user,
                    subject=subject,
                    date=date,
                    defaults={'status': status, 'marked_by': request.user}
                )
        
        messages.success(request, "Attendance marked successfully.")
        
        # Check low attendance and send email
        for student_profile in students:
            total = Attendance.objects.filter(student=student_profile.user, subject=subject).count()
            if total > 0:
                present = Attendance.objects.filter(student=student_profile.user, subject=subject, status='PRESENT').count()
                percentage = (present / total) * 100
                if percentage < 75: # Low attendance threshold
                     send_mail(
                        'Low Attendance Warning',
                        f'Your ward {student_profile.user.first_name} has low attendance in {subject.name} ({percentage:.1f}%).',
                        'admin@mentordesk.com',
                        [student_profile.parent_email],
                        fail_silently=True,
                    )

        return redirect('faculty_dashboard')

class SubjectCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Subject
    fields = ['name', 'assigned_class', 'semester']
    template_name = 'academics/subject_form.html'
    success_url = reverse_lazy('faculty_dashboard')

    def test_func(self):
        return self.request.user.is_faculty

    def form_valid(self, form):
        form.instance.faculty = self.request.user
        messages.success(self.request, "Subject added successfully.")
        return super().form_valid(form)

class AchievementCreateView(LoginRequiredMixin, CreateView):
    model = Achievement
    fields = ['title', 'description', 'certificate']
    template_name = 'academics/achievement_form.html'
    success_url = reverse_lazy('student_dashboard')

    def form_valid(self, form):
        form.instance.student = self.request.user
        messages.success(self.request, "Achievement submitted.")
        return super().form_valid(form)

class SendNotificationView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_mentor

    def get(self, request):
        classes = Class.objects.filter(mentors=request.user)
        return render(request, 'academics/send_notification.html', {'classes': classes})

    def post(self, request):
        class_id = request.POST.get('class_id')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        assigned_class = get_object_or_404(Class, id=class_id, mentors=request.user)
        students = StudentProfile.objects.filter(assigned_class=assigned_class)
        emails = [s.user.email for s in students if s.user.email]
        
        if emails:
            send_mail(
                subject,
                message,
                'mentor@mentordesk.com',
                emails,
                fail_silently=True,
            )
            
            # Create in-app notifications
            for student in students:
                Notification.objects.create(
                    recipient=student.user,
                    sender=request.user,
                    title=subject,
                    message=message
                )
                
            messages.success(request, f"Notification sent to {len(emails)} students.")
        else:
            messages.warning(request, "No students with email addresses found in this class.")
            
        return redirect('mentor_dashboard')

class StudentAttendanceView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'academics/student_attendance.html'

    def test_func(self):
        return self.request.user.is_student

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user
        profile = student.student_profile
        semester_subjects = Subject.objects.filter(assigned_class=profile.assigned_class, semester=profile.semester)
        
        # Detailed attendance records
        context['attendance_records'] = Attendance.objects.filter(student=student, subject__in=semester_subjects).order_by('-date')
        
        # Subject-wise attendance
        subject_data = []
        for subject in semester_subjects:
            total = Attendance.objects.filter(student=student, subject=subject).count()
            present = Attendance.objects.filter(student=student, subject=subject, status='PRESENT').count()
            percentage = (present / total * 100) if total > 0 else 0
            subject_data.append({
                'subject': subject.name,
                'total': total,
                'present': present,
                'percentage': percentage
            })
        context['subject_data'] = subject_data
        
        return context

class StudentStartAchievementView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Achievement
    template_name = 'academics/student_achievements.html'
    context_object_name = 'achievements'

    def test_func(self):
        return self.request.user.is_student

    def get_queryset(self):
        return Achievement.objects.filter(student=self.request.user).order_by('-submitted_on')
