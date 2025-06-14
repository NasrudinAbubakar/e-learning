from django.urls import path
from .views import index, Explore_Courses, Featured_Instructors, Learning_Path

urlpatterns = [
    path('', index, name='index'),
    path('explore-courses/', Explore_Courses, name='explore_courses'),
    path('featured-instructors/', Featured_Instructors, name='featured_instructors'),
    path('learning-paths/', Learning_Path, name='learning_path'),
]
