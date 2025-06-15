from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify

class Instructor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='instructor_profile')
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    # any other instructor-specific fields

    @property
    def average_rating(self):
        # aggregate over all reviews of all this instructor’s courses
        return (self.courses
                    .annotate(nullptr=models.Value(None))  # workaround for chaining
                    .aggregate(avg=Avg('reviews__rating'))
                    ['avg'] or 0)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


from django.core.validators import MinValueValidator, MaxValueValidator

class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)  # new slug field
    description = models.TextField()
    instructor = models.ForeignKey(Instructor,
                                   on_delete=models.CASCADE,
                                   related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

class Review(models.Model):
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='reviews')
    student = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'student')

    def __str__(self):
        return f"{self.rating} by {self.student} on {self.course}"
