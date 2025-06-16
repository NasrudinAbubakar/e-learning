from django.contrib import admin
from .models import (
    Instructor, Course, Review, Category,
    Section, Lecture, LectureResource,
    Enrollment, CompletedLecture, Certificate
)

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('user', 'average_rating')
    readonly_fields = ('average_rating',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'created_at')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'rating', 'created_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('course', 'order', 'title')
    ordering = ('course', 'order')

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('section', 'order', 'title', 'lecture_type', 'is_preview')
    ordering = ('section', 'order')

@admin.register(LectureResource)
class LectureResourceAdmin(admin.ModelAdmin):
    list_display = ('lecture', 'order', 'title')
    ordering = ('lecture', 'order')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'is_active')
    ordering = ('course', 'enrolled_at')

@admin.register(CompletedLecture)
class CompletedLectureAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lecture', 'completed_at')
    ordering = ('enrollment', 'completed_at')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'certificate_id', 'issued_at')
    ordering = ('issued_at',)
