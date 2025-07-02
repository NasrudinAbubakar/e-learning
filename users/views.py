from django.forms import formset_factory, inlineformset_factory
from django.views.generic import TemplateView
from django.views.generic import CreateView
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, 
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.views import View
from django.urls import reverse_lazy
from .forms import CourseForm, LectureForm, LoginForm, SectionForm, SectionFormSet, LectureFormSet, SignUpForm
from .models import Course, InstructorRequest, Section, Lecture, Student
# Create your views here.


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Authenticate using email as username
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Check approved instructor status
                if hasattr(user, 'instructor_profile') and user.instructor_profile.approved:
                    messages.success(request, f"Welcome back, Instructor {user.first_name}!")
                    return redirect('instructor_dashboard')
                
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect('student_dashboard')
            
            # Authentication failed
            form.add_error(None, "Invalid email or password")
            messages.error(request, "Login failed. Please check your credentials.")
    else:
        form = LoginForm()
    
    return render(request, 'users/auth/login.html', {'form': form})



User = get_user_model()

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']  # Use email as username
            user.save()
            
            # Create student profile by default
            Student.objects.create(user=user)
            
            # If signing up as instructor, create request
            if form.cleaned_data.get('account_type') == 'instructor':
                InstructorRequest.objects.create(
                    user=user,
                    motivation=form.cleaned_data.get('motivation', ''),
                    qualifications=form.cleaned_data.get('qualifications', '')
                )
                messages.info(request, "Your instructor request has been submitted for approval")
            
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')  # Redirect to a generic dashboard first
            
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'

class InstructorRequiredMixin(LoginRequiredMixin):
    """Verify that the current user is authenticated and is an instructor."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not hasattr(request.user, 'instructor_profile'):
            raise PermissionDenied("This page is only accessible to instructors.")
        return super().dispatch(request, *args, **kwargs)


class StudentDashboardView(TemplateView):
    template_name = "users/student_dashboard.html"
    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["sidebar_template"] = "users/sidebar_student.html"
        return ctx

class InstructorDashboardView(InstructorRequiredMixin, TemplateView):
    template_name = "users/instructor_dashboard.html"
    
    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["sidebar_template"] = "users/sidebar_instructor.html"
        return ctx

class InstructorCreateCourseView(InstructorRequiredMixin, View):
    template_name = "users/create_course.html"

    def get(self, request, *args, **kwargs):
        course_form = CourseForm()
        SectionFormSet = inlineformset_factory(
            Course, 
            Section, 
            form=SectionForm, 
            extra=1, 
            can_delete=True
        )
        section_formset = SectionFormSet(prefix="sections")
        
        # Initialize empty lecture formsets for each section
        LectureFormSet = inlineformset_factory(
            Section, 
            Lecture,
            form=LectureForm,
            extra=1,
            can_delete=True
        )
        lecture_formsets = [
            LectureFormSet(prefix=f"lectures-{i}") 
            for i in range(section_formset.total_form_count())
        ]
        
        context = {
            "form": course_form,
            "section_formset": section_formset,
            "lecture_formsets": lecture_formsets,
            "sidebar_template": "users/sidebar_instructor.html",
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        course_form = CourseForm(request.POST, request.FILES)
        SectionFormSet = inlineformset_factory(
            Course, 
            Section,
            form=SectionForm,
            extra=0,
            can_delete=True
        )
        section_formset = SectionFormSet(
            request.POST,
            prefix="sections"
        )
        
        # Get lecture formsets for each section
        lecture_formsets = []
        total_sections = int(request.POST.get('sections-TOTAL_FORMS', 0))
        
        LectureFormSet = inlineformset_factory(
            Section, 
            Lecture,
            form=LectureForm,
            extra=0,
            can_delete=True
        )
        
        for i in range(total_sections):
            lecture_formsets.append(
                LectureFormSet(
                    request.POST, 
                    request.FILES,
                    prefix=f"lectures-{i}"
                )
            )
        
        if course_form.is_valid() and section_formset.is_valid():
            lecture_forms_valid = all([formset.is_valid() for formset in lecture_formsets])
            
            if lecture_forms_valid:
                # Save course with the logged-in instructor
                course = course_form.save(commit=False)
                course.instructor = request.user.instructor_profile
                course.save()

                # Save sections
                for i, section_form in enumerate(section_formset):
                    if section_form.cleaned_data and not section_form.cleaned_data.get('DELETE', False):
                        section = section_form.save(commit=False)
                        section.course = course
                        section.save()
                        
                        # Save lectures for this section
                        lecture_formset = lecture_formsets[i]
                        for lecture_form in lecture_formset:
                            if lecture_form.cleaned_data and not lecture_form.cleaned_data.get('DELETE', False):
                                lecture = lecture_form.save(commit=False)
                                lecture.section = section
                                if lecture_form.cleaned_data.get('content'):
                                    lecture.content = lecture_form.cleaned_data['content']
                                lecture.save()

                messages.success(request, "Course created successfully!")
                return redirect("users:instructor_course_manage")
            else:
                messages.error(request, "Please correct the errors in the lecture forms")
        else:
            messages.error(request, "Please correct the errors below")

        context = {
            "form": course_form,
            "section_formset": section_formset,
            "lecture_formsets": lecture_formsets,
            "sidebar_template": "users/sidebar_instructor.html",
        }
        return render(request, self.template_name, context)

class InstructorCreateManageView(InstructorRequiredMixin, TemplateView):
    template_name = "users/course_manage.html"   
    
    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["sidebar_template"] = "users/sidebar_instructor.html"
        # Add instructor's courses to context
        ctx["courses"] = Course.objects.filter(instructor=self.request.user.instructor_profile)
        return ctx

class InstructorAnalyticsView(InstructorRequiredMixin, TemplateView):
    template_name = "users/instructor_analytics.html"   
    
    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["sidebar_template"] = "users/sidebar_instructor.html"
        return ctx



class BecomeInstructorView(LoginRequiredMixin, CreateView):
    model = InstructorRequest
    fields = ['motivation', 'qualifications']
    template_name = 'become_instructor.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        if hasattr(self.request.user, 'instructor_profile'):
            messages.warning(self.request, "You are already an instructor!")
            return redirect('dashboard')
        messages.success(self.request, "Your instructor request has been submitted!")
        return super().form_valid(form)