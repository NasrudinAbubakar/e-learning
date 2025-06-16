from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .forms import CourseForm, SectionFormSet, LectureFormSet

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

class InstructorCreateCourseView(View):
    template_name = "users/create_course.html"

    def get(self, request, *args, **kwargs):
        course_form = CourseForm()
        section_formset = SectionFormSet(prefix="sections")
        # Attach an empty LectureFormSet to each section form for rendering in the template
        for i, form in enumerate(section_formset.forms):
            form.lecture_formset = LectureFormSet(prefix=f"lectures_{i}", instance=form.instance)
        context = {
            "form": course_form,
            "section_formset": section_formset,
            "sidebar_template": "users/sidebar_instructor.html",
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        course_form = CourseForm(request.POST, request.FILES)
        section_formset = SectionFormSet(request.POST, prefix="sections")
        lecture_formsets = []  # container for lecture formsets
        if course_form.is_valid() and section_formset.is_valid():
            course = course_form.save(commit=False)
            course.instructor = request.user.instructor_profile  # adjust as needed
            course.save()

            sections = section_formset.save(commit=False)
            # Process each section and its lecture formset
            for i, section in enumerate(sections):
                section.course = course
                section.save()
                lecture_formset = LectureFormSet(
                    request.POST, request.FILES,
                    prefix=f"lectures_{i}",
                    instance=section
                )
                lecture_formsets.append(lecture_formset)
                if lecture_formset.is_valid():
                    lecture_formset.save()
                else:
                    # On error, reattach lecture_formsets to their respective section forms
                    for j, form in enumerate(section_formset.forms):
                        form.lecture_formset = (
                            lecture_formset if j == i
                            else LectureFormSet(
                                request.POST, request.FILES,
                                prefix=f"lectures_{j}", instance=form.instance
                            )
                        )
                    context = {
                        "form": course_form,
                        "section_formset": section_formset,
                        "sidebar_template": "users/sidebar_instructor.html",
                    }
                    return render(request, self.template_name, context)

            messages.success(request, "Course created successfully!")
            return redirect("users:instructor_course_manage")
        else:
            # Reattach lecture formsets to each section form upon errors
            for i, form in enumerate(section_formset.forms):
                form.lecture_formset = LectureFormSet(
                    request.POST, request.FILES,
                    prefix=f"lectures_{i}",
                    instance=form.instance
                )
        context = {
            "form": course_form,
            "section_formset": section_formset,
            "sidebar_template": "users/sidebar_instructor.html",
        }
        return render(request, self.template_name, context)

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

