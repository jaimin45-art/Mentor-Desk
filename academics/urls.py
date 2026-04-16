from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/student/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('dashboard/mentor/', views.MentorDashboardView.as_view(), name='mentor_dashboard'),
    path('dashboard/faculty/', views.FacultyDashboardView.as_view(), name='faculty_dashboard'),
    path('dashboard/parent/', views.ParentDashboardView.as_view(), name='parent_dashboard'),
    
    path('student/attendance/', views.StudentAttendanceView.as_view(), name='student_attendance_detail'),
    path('student/achievements/', views.StudentStartAchievementView.as_view(), name='student_achievements_detail'),
    
    path('leave/apply/', views.LeaveCreateView.as_view(), name='leave_apply'),
    path('leave/approve/<int:pk>/', views.LeaveApprovalView.as_view(), name='leave_review'),
    
    path('subject/add/', views.SubjectCreateView.as_view(), name='subject_add'),
    path('attendance/mark/<int:subject_id>/', views.MarkAttendanceView.as_view(), name='mark_attendance'),
    
    path('achievement/submit/', views.AchievementCreateView.as_view(), name='achievement_submit'),
    path('notification/send/', views.SendNotificationView.as_view(), name='send_notification'),
]
