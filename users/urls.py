from django.urls import path
from .views import StudentDashboardView, InstructorCreateCourseView, InstructorDashboardView, InstructorCreateManageView, InstructorAnalyticsView

app_name = "users"
urlpatterns = [
    path("dashboard/student/", StudentDashboardView.as_view(), name="student_dashboard"),
    path("dashboard/instructor/", InstructorDashboardView.as_view(), name="instructor_dashboard"),
    path("dashboard/instructor/analytics/", InstructorAnalyticsView.as_view(), name="instructor_analytics"),
    path("dashboard/instructor/create-course/", InstructorCreateCourseView.as_view(), name="instructor_create_course"),
    path("dashboard/instructor/course-manage/", InstructorCreateManageView.as_view(), name="instructor_course_manage"),
]
