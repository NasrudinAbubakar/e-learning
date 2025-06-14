from django.views.generic import TemplateView
from django.shortcuts import render

# Create your views here.

class StudentDashboardView(TemplateView):
    template_name = "users/student_dashboard.html"
    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["sidebar_template"] = "users/sidebar_student.html"
        return ctx

class InstructorDashboardView(TemplateView):
    template_name = "users/instructor_dashboard.html"
    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["sidebar_template"] = "users/sidebar_instructor.html"
        return ctx

class InstructorCreateCourseView(TemplateView):
    template_name = "users/create_course.html"   
    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["sidebar_template"] = "users/sidebar_instructor.html"
        return ctx

class InstructorCreateManageView(TemplateView):
    template_name = "users/course_manage.html"   
    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["sidebar_template"] = "users/sidebar_instructor.html"
        return ctx

class InstructorAnalyticsView(TemplateView):
    template_name = "users/instructor_analytics.html"   
    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["sidebar_template"] = "users/sidebar_instructor.html"
        return ctx

