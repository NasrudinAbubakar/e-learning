# yourapp/forms.py
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import Course, Section, Lecture
from .widgets import MultipleFileInput

COMMON_INPUT_CLASS = 'form-control'
COMMON_SELECT_CLASS = 'form-control form-select'
COMMON_TEXTAREA_CLASS = 'form-control form-textarea'
CHECKBOX_CLASS = 'checkbox-input'
FILE_UPLOAD_CLASS = 'file-upload'

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title', 'slug', 'subtitle', 'description', 'category',
            'thumbnail', 'promo_video',
            'price', 'discount_price',
            'language', 'difficulty', 'has_certificate', 'published',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': COMMON_INPUT_CLASS,
                'id': 'course-title',
                'placeholder': 'e.g. Advanced JavaScript Patterns',
            }),
            'slug': forms.TextInput(attrs={
                'class': COMMON_INPUT_CLASS,
                'readonly': 'readonly',
                'placeholder': 'Auto-generated from title',
            }),
            'subtitle': forms.TextInput(attrs={
                'class': COMMON_INPUT_CLASS,
                'id': 'course-subtitle',
                'placeholder': 'What will students learn in your course?',
            }),
            'description': forms.Textarea(attrs={
                'class': COMMON_TEXTAREA_CLASS,
                'id': 'course-description',
                'rows': 4,
                'placeholder': 'Describe your course in detail',
            }),
            'category': forms.Select(attrs={
                'class': COMMON_SELECT_CLASS,
                'id': 'course-category',
            }),
            'thumbnail': forms.ClearableFileInput(attrs={
                'class': FILE_UPLOAD_CLASS,
                'id': 'thumbnail-upload',
            }),
            'promo_video': forms.ClearableFileInput(attrs={
                'class': FILE_UPLOAD_CLASS,
                'id': 'video-upload',
            }),
            'price': forms.NumberInput(attrs={
                'class': COMMON_INPUT_CLASS,
                'id': 'course-price',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00',
            }),
            'discount_price': forms.NumberInput(attrs={
                'class': COMMON_INPUT_CLASS,
                'placeholder': '0.00',
            }),
            'language': forms.Select(attrs={
                'class': COMMON_SELECT_CLASS,
                'id': 'course-language',
            }),
            'difficulty': forms.Select(attrs={
                'class': COMMON_SELECT_CLASS,
                'id': 'course-level',
            }),
            'has_certificate': forms.CheckboxInput(attrs={
                'class': CHECKBOX_CLASS,
                'id': 'certificate',
                'checked': True,
            }),
            'published': forms.HiddenInput(),  # We'll handle publishing separately
        }
        labels = {
            'title': 'Course Title',
            'subtitle': 'Subtitle',
            'description': 'Description',
            'category': 'Category',
            'thumbnail': 'Course Thumbnail',
            'promo_video': 'Promotional Video (Optional)',
            'price': 'Course Price',
            'language': 'Language',
            'difficulty': 'Difficulty Level',
            'certificate': 'Include certificate of completion',
        }
        help_texts = {
            'title': 'Keep it concise yet descriptive (60 characters or less)',
            'subtitle': 'A brief summary of your course (120 characters or less)',
            'description': 'This will appear on your course landing page',
            'thumbnail': 'Recommended size: 1280×720 pixels (16:9 aspect ratio)',
            'promo_video': 'MP4 format, max 2 minutes, 1080p recommended',
        }

    # Add discount option field (not in model, just for form)
    discount_option = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': CHECKBOX_CLASS,
            'id': 'discount-course',
        }),
        label='Offer discount'
    )

    # Add free course option field (not in model, just for form)
    free_course = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': CHECKBOX_CLASS,
            'id': 'free-course',
        }),
        label='This is a free course'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for our custom fields
        if self.instance:
            self.fields['free_course'].initial = self.instance.price == 0
            self.fields['discount_option'].initial = bool(self.instance.discount_price)

    def clean(self):
        cleaned_data = super().clean()
        free_course = cleaned_data.get('free_course')
        price = cleaned_data.get('price')
        discount_option = cleaned_data.get('discount_option')
        discount_price = cleaned_data.get('discount_price')

        if free_course and price != 0:
            self.add_error('price', 'Price must be 0 for free courses')
            self.add_error('free_course', '')

        if discount_option and not discount_price:
            self.add_error('discount_price', 'Please set a discount price')
        elif discount_option and discount_price >= price:
            self.add_error('discount_price', 'Discount price must be less than regular price')

        return cleaned_data

    def clean_thumbnail(self):
        thumb = self.cleaned_data.get('thumbnail')
        if thumb:
            from PIL import Image
            try:
                img = Image.open(thumb)
                if img.width < 1280 or img.height < 720:
                    raise ValidationError("Thumbnail must be at least 1280×720 pixels.")
            except:
                raise ValidationError("Invalid image file. Please upload a valid image.")
        return thumb

    def clean_promo_video(self):
        video = self.cleaned_data.get('promo_video')
        if video:
            if not video.name.lower().endswith('.mp4'):
                raise ValidationError("Promo video must be MP4 format.")
            if video.size > 50 * 1024 * 1024:  # 50MB
                raise ValidationError("Promo video must be under 50 MB.")
        return video


class BaseSectionFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        if not any(form.cleaned_data and not form.cleaned_data.get('DELETE', False)
                   for form in self.forms):
            raise ValidationError("You must add at least one section.")


SectionFormSet = inlineformset_factory(
    Course, Section,
    formset=BaseSectionFormSet,
    fields=('order', 'title'),
    widgets={
        'order': forms.NumberInput(attrs={'class': COMMON_INPUT_CLASS}),
        'title': forms.TextInput(attrs={'class': COMMON_INPUT_CLASS}),
    },
    extra=1, 
    can_delete=True
)


class BaseLectureFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        if not any(form.cleaned_data and not form.cleaned_data.get('DELETE', False)
                   for form in self.forms):
            raise ValidationError("Each section needs at least one lecture.")


LectureFormSet = inlineformset_factory(
    Section, Lecture,
    formset=BaseLectureFormSet,
    fields=('order', 'title', 'content', 'video_url', 'duration_minutes', 'lecture_type', 'is_preview'),
    widgets={
        'order': forms.NumberInput(attrs={'class': COMMON_INPUT_CLASS}),
        'title': forms.TextInput(attrs={'class': COMMON_INPUT_CLASS}),
        'content': forms.ClearableFileInput(attrs={'class': FILE_UPLOAD_CLASS}),
        'video_url': forms.URLInput(attrs={'class': COMMON_INPUT_CLASS}),
        'duration_minutes': forms.NumberInput(attrs={'class': COMMON_INPUT_CLASS}),
        'lecture_type': forms.Select(attrs={'class': COMMON_SELECT_CLASS}),
        'is_preview': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
    },
    extra=1, 
    can_delete=True
)