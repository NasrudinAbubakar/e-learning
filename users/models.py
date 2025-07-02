from django.conf import settings
from django.db import models
from django.db.models import Avg, Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.urls import reverse



class InstructorRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instructor_requests'
    )
    motivation = models.TextField(help_text="Why do you want to become an instructor?")
    qualifications = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def approve(self):
        Instructor.objects.get_or_create(user=self.user)
        self.status = 'approved'
        self.save()

    def __str__(self):
        return f"Instructor request from {self.user.username}"

class Instructor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instructor_profile'
    )
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    profile_picture = models.ImageField(
        upload_to='instructor_profiles/',
        blank=True,
        null=True
    )

    @property
    def average_rating(self):
        return (
            self.courses
            .aggregate(avg=Avg('reviews__rating'))
            ['avg'] or 0
        )

    @property
    def courses_count(self):
        return self.courses.count()

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    def get_absolute_url(self):
        return reverse('instructor_detail', kwargs={'pk': self.pk})


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to='student_profiles/',
        blank=True,
        null=True
    )
    # Add any additional student-specific fields here

    def __str__(self):
        return f"Student profile for {self.user.username}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Font Awesome icon class (e.g. 'fas fa-code')"
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Language(models.TextChoices):
    SOMALI = 'so', _('Somali')
    ENGLISH = 'en', _('English')
    ARABIC = 'ar', _('Arabic')
    # add more as needed


class DifficultyLevel(models.TextChoices):
    BEGINNER = 'beginner', _('Beginner')
    INTERMEDIATE = 'intermediate', _('Intermediate')
    ADVANCED = 'advanced', _('Advanced')
    ALL_LEVELS = 'all', _('All Levels')


class Course(models.Model):
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name='courses'
    )

    # — Basic Info —
    title = models.CharField(
        max_length=60,
        help_text="Keep it concise yet descriptive (60 chars or less)"
    )
    slug = models.SlugField(
        max_length=75,
        unique=True,
        help_text="URL fragment, auto-generated from title if blank"
    )
    subtitle = models.CharField(
        max_length=120,
        help_text="A brief summary (120 chars or less)"
    )
    description = models.TextField(
        help_text="Describe your course in detail; appears on landing page"
    )
    objectives = models.TextField(
        blank=True,
        help_text="What will students learn? (Bullet points recommended)"
    )
    requirements = models.TextField(
        blank=True,
        help_text="Prerequisites or requirements for this course"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses'
    )

    # — Media —
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/',
        help_text="1280×720px (16:9) recommended"
    )
    promo_video = models.FileField(
        upload_to='course_trailers/',
        blank=True, null=True,
        help_text="MP4, max 2 minutes, 1080p recommended"
    )

    # — Pricing —
    price = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True, null=True,
        help_text="Optional discounted price"
    )

    # — Additional Settings —
    language = models.CharField(
        max_length=5,
        choices=Language.choices,
        default=Language.SOMALI
    )
    difficulty = models.CharField(
        max_length=12,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER
    )
    certificate_template = models.ImageField(
        upload_to='certificate_templates/',
        blank=True, null=True,
        help_text="Certificate template (optional)"
    )
    has_certificate = models.BooleanField(
        default=True,
        verbose_name="Include certificate"
    )

    # — Metadata —
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:70]
            slug_candidate = base
            n = 1
            while Course.objects.filter(slug=slug_candidate).exists():
                slug_candidate = f"{base}-{n}"
                n += 1
            self.slug = slug_candidate
        
        # Ensure discount price is null if not used
        if not self.discount_price:
            self.discount_price = None
            
        super().save(*args, **kwargs)

    def clean(self):
        if self.discount_price and self.discount_price >= self.price:
            raise ValidationError(
                "Discount price must be less than the regular price."
            )

    @property
    def is_free(self):
        return self.price == 0

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def duration(self):
        """Calculate total course duration in minutes"""
        total = sum(lecture.duration_minutes for section in self.sections.all() 
                   for lecture in section.lectures.all())
        return total

    @property
    def average_rating(self):
        return self.reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    @property
    def students_count(self):
        return self.enrollments.count()

    @property
    def lectures_count(self):
        return Lecture.objects.filter(section__course=self).count()

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class Section(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('course', 'order')
        ordering = ['order']
        verbose_name = "Section"
        verbose_name_plural = "Sections"

    @property
    def lectures_count(self):
        return self.lectures.count()

    def __str__(self):
        return f"{self.course.title} – {self.title}"


class Lecture(models.Model):
    LECTURE_TYPES = (
        ('video', 'Video'),
        ('article', 'Article'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='lectures'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = models.FileField(
        upload_to='lecture_content/',
        blank=True,
        null=True,
        help_text="Video, PDF, etc."
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="External video URL (YouTube, Vimeo, etc.)"
    )
    duration_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Duration in minutes"
    )
    lecture_type = models.CharField(
        max_length=20,
        choices=LECTURE_TYPES,
        default='video'
    )
    is_preview = models.BooleanField(
        default=False,
        help_text="Available for preview without enrollment"
    )
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('section', 'order')
        ordering = ['order']
        verbose_name = "Lecture"
        verbose_name_plural = "Lectures"

    def clean(self):
        if not self.content and not self.video_url:
            raise ValidationError(
                "Either content file or video URL must be provided."
            )

    def __str__(self):
        return f"{self.section.title} – {self.title}"


class LectureResource(models.Model):
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='lecture_resources/')
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        verbose_name = "Resource"
        verbose_name_plural = "Resources"

    def __str__(self):
        return f"{self.lecture.title} – {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'course')
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    @property
    def progress(self):
        total_lectures = self.course.lectures_count
        if total_lectures == 0:
            return 0
        completed = self.completed_lectures.count()
        return (completed / total_lectures) * 100

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


class CompletedLecture(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='completed_lectures'
    )
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('enrollment', 'lecture')
        verbose_name = "Completed Lecture"
        verbose_name_plural = "Completed Lectures"

    def __str__(self):
        return f"{self.enrollment.student} completed {self.lecture}"


class Review(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'student')
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def clean(self):
        # Ensure only enrolled students can review
        if not Enrollment.objects.filter(
            student=self.student,
            course=self.course
        ).exists():
            raise ValidationError(
                "You must be enrolled in the course to leave a review."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rating} by {self.student} on {self.course}"


class Certificate(models.Model):
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='certificate'
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_id = models.CharField(max_length=20, unique=True)
    pdf_file = models.FileField(
        upload_to='certificates/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CERT-{self.enrollment.course.id}-{self.enrollment.id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificate for {self.enrollment.student} in {self.enrollment.course}"




@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profiles(sender, instance, created, **kwargs):
    if created:
        # Every user gets a student profile by default
        Student.objects.get_or_create(user=instance)

@receiver(post_save, sender=InstructorRequest)
def handle_instructor_approval(sender, instance, created, **kwargs):
    if instance.status == 'approved' and not hasattr(instance.user, 'instructor_profile'):
        Instructor.objects.create(user=instance.user)