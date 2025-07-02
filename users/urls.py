from django.shortcuts import redirect
from django.urls import path
from .views import BecomeInstructorView, StudentDashboardView, InstructorCreateCourseView, InstructorDashboardView, InstructorCreateManageView, InstructorAnalyticsView

app_name = "users"
urlpatterns = [
    path("dashboard/student/", StudentDashboardView.as_view(), name="student_dashboard"),
    path("dashboard/instructor/", InstructorDashboardView.as_view(), name="instructor_dashboard"),
    path("dashboard/instructor/analytics/", InstructorAnalyticsView.as_view(), name="instructor_analytics"),
    path("dashboard/instructor/create-course/", InstructorCreateCourseView.as_view(), name="instructor_create_course"),
    path("dashboard/instructor/course-manage/", InstructorCreateManageView.as_view(), name="instructor_course_manage"),
    path('become-instructor/', BecomeInstructorView.as_view(), name='become_instructor'),
]
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    BecomeInstructorView,
    StudentDashboardView,
    InstructorCreateCourseView,
    InstructorDashboardView,
    InstructorCreateManageView,
    InstructorAnalyticsView,
    # Add these new views
    # InstructorRequestStatusView,
    # ToggleInstructorModeView,
    # InstructorProfileUpdateView,
    # StudentProfileUpdateView,
)

app_name = "users"

urlpatterns = [
    # Dashboard Routes
    path("dashboard/student/", StudentDashboardView.as_view(), name="student_dashboard"),
    path("dashboard/instructor/", InstructorDashboardView.as_view(), name="instructor_dashboard"),
    
    # Instructor-Specific Routes
    path("dashboard/instructor/analytics/", InstructorAnalyticsView.as_view(), name="instructor_analytics"),
    path("dashboard/instructor/create-course/", InstructorCreateCourseView.as_view(), name="instructor_create_course"),
    path("dashboard/instructor/course-manage/", InstructorCreateManageView.as_view(), name="instructor_course_manage"),
    
    #path("dashboard/instructor/profile/", InstructorProfileUpdateView.as_view(), name="instructor_profile_update"),
    
    # Student-Specific Routes
    #path("dashboard/student/profile/", StudentProfileUpdateView.as_view(), name="student_profile_update"),
    
    # Role Management Routes
    # path('become-instructor/', BecomeInstructorView.as_view(), name='become_instructor'),
    # path('instructor-request/status/', InstructorRequestStatusView.as_view(), name='instructor_request_status'),
    # path('toggle-instructor-mode/', ToggleInstructorModeView.as_view(), name='toggle_instructor_mode'),
    
    # Authentication Routes (if not using Django's built-in auth URLs)
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # Redirect root to appropriate dashboard
    path("", lambda request: redirect(
        'users:instructor_dashboard' if hasattr(request.user, 'instructor_profile') 
        else 'users:student_dashboard'
    ), name="dashboard_redirect"),
]