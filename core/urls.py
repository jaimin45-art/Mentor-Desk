from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.UnifiedRegisterView.as_view(), name='unified_register'),
    # Kept old paths for backwards compatibility if needed, but 'register' now points to unified
    path('register/student/', views.StudentRegisterView.as_view(), name='register_student'),
    path('register/mentor/', views.MentorRegisterView.as_view(), name='register_mentor'),
    path('register/faculty/', views.FacultyRegisterView.as_view(), name='register_faculty'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
