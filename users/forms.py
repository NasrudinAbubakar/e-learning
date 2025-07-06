# yourapp/forms.py
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from PIL import Image
from .models import Course, InstructorRequest, Section, Lecture

COMMON_INPUT_CLASS = 'form-control'
COMMON_SELECT_CLASS = 'form-control form-select'
COMMON_TEXTAREA_CLASS = 'form-control form-textarea'
CHECKBOX_CLASS = 'checkbox-input'
FILE_UPLOAD_CLASS = 'file-upload'


User = get_user_model()

class SignUpForm(UserCreationForm):
    ACCOUNT_TYPES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )
    
    account_type   = forms.ChoiceField(choices=ACCOUNT_TYPES)
    email          = forms.EmailField(required=True)
    first_name     = forms.CharField(required=True)
    last_name      = forms.CharField(required=True)
    motivation     = forms.CharField(
        required=False,
        widget=forms.Textarea,
        help_text="Why do you want to become an instructor?"
    )
    qualifications = forms.CharField(
        required=False,
        widget=forms.Textarea,
        help_text="Your relevant qualifications or experience"
    )

    class Meta:
        model  = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('account_type') == 'instructor':
            if not cleaned_data.get('motivation'):
                self.add_error('motivation', "Please explain why you want to become an instructor")
            if not cleaned_data.get('qualifications'):
                self.add_error('qualifications', "Please describe your qualifications")
        return cleaned_data

    def save(self, commit=True):
        # Build the user but don’t save to DB yet
        user = super().save(commit=False)
        user.username   = self.cleaned_data['email']
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title', 'slug', 'subtitle', 'description', 'objectives', 'requirements', 'category',
            'thumbnail', 'promo_video', 'price', 'discount_price',
            'language', 'difficulty', 'certificate_template', 'has_certificate', 'published', 'featured',
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
            'objectives': forms.Textarea(attrs={
                'class': COMMON_TEXTAREA_CLASS,
                'id': 'course-objectives',
                'rows': 3,
                'placeholder': 'List the learning objectives (one per line)',
            }),
            'requirements': forms.Textarea(attrs={
                'class': COMMON_TEXTAREA_CLASS,
                'id': 'course-requirements',
                'rows': 2,
                'placeholder': 'List any prerequisites or requirements',
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
            'certificate_template': forms.ClearableFileInput(attrs={
                'class': FILE_UPLOAD_CLASS,
                'id': 'certificate-template-upload',
            }),
            'has_certificate': forms.CheckboxInput(attrs={
                'class': CHECKBOX_CLASS,
                'id': 'certificate',
                'checked': True,
            }),
            'published': forms.HiddenInput(),
            'featured': forms.CheckboxInput(attrs={
                'class': CHECKBOX_CLASS,
                'id': 'featured',
            }),
        }
        labels = {
            'title': 'Course Title',
            'subtitle': 'Subtitle',
            'description': 'Description',
            'objectives': 'Learning Objectives',
            'requirements': 'Requirements',
            'category': 'Category',
            'thumbnail': 'Course Thumbnail',
            'promo_video': 'Promotional Video (Optional)',
            'price': 'Course Price',
            'discount_price': 'Discount Price',
            'language': 'Language',
            'difficulty': 'Difficulty Level',
            'certificate_template': 'Certificate Template (Optional)',
            'has_certificate': 'Include certificate of completion',
            'featured': 'Feature this course',
        }
        help_texts = {
            'title': 'Keep it concise yet descriptive (60 characters or less)',
            'subtitle': 'A brief summary of your course (120 characters or less)',
            'description': 'This will appear on your course landing page',
            'objectives': 'What will students learn? (Bullet points recommended)',
            'requirements': 'Prerequisites or requirements for this course',
            'thumbnail': 'Recommended size: 1280×720 pixels (16:9 aspect ratio)',
            'promo_video': 'MP4 format, max 2 minutes, 1080p recommended',
            'certificate_template': 'Upload a custom certificate template (optional)',
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
        # Set initial values for our custom fields only if instance exists and has been saved
        if self.instance and self.instance.pk:
            self.fields['free_course'].initial = self.instance.price == 0
            self.fields['discount_option'].initial = bool(self.instance.discount_price)

    def clean(self):
        cleaned_data = super().clean()
        free_course = cleaned_data.get('free_course')
        price = cleaned_data.get('price')
        discount_option = cleaned_data.get('discount_option')
        discount_price = cleaned_data.get('discount_price')

        # Handle free course logic
        if free_course:
            cleaned_data['price'] = 0  # Automatically set price to 0 for free courses
        elif price == 0 and not free_course:
            # If price is 0 but free_course is not checked, this might be intentional
            # You can add a warning or handle as needed
            pass

        # Handle discount validation
        if discount_option:
            if not discount_price:
                self.add_error('discount_price', 'Please set a discount price when offering a discount')
            elif price and discount_price >= price:
                self.add_error('discount_price', 'Discount price must be less than regular price')
        else:
            # Clear discount price if discount option is not selected
            cleaned_data['discount_price'] = None

        return cleaned_data

    def clean_thumbnail(self):
        thumb = self.cleaned_data.get('thumbnail')
        if thumb:
            try:
                img = Image.open(thumb)
                if img.width < 1280 or img.height < 720:
                    raise ValidationError("Thumbnail must be at least 1280×720 pixels.")
            except (IOError, OSError) as e:
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


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['order', 'title', 'description']
        widgets = {
            'order': forms.NumberInput(attrs={'class': COMMON_INPUT_CLASS}),
            'title': forms.TextInput(attrs={'class': COMMON_INPUT_CLASS}),
            'description': forms.Textarea(attrs={
                'class': COMMON_TEXTAREA_CLASS,
                'rows': 2,
                'placeholder': 'Describe this section (optional)',
            }),
        }
        labels = {
            'order': 'Order',
            'title': 'Section Title',
            'description': 'Section Description',
        }
        help_texts = {
            'description': 'Optional: Add a description for this section.',
        }


class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['order', 'title', 'content', 'video_url', 'duration_minutes', 'lecture_type', 'is_preview']
        widgets = {
            'order': forms.NumberInput(attrs={'class': COMMON_INPUT_CLASS}),
            'title': forms.TextInput(attrs={'class': COMMON_INPUT_CLASS}),
            'content': forms.ClearableFileInput(attrs={'class': FILE_UPLOAD_CLASS}),
            'video_url': forms.URLInput(attrs={'class': COMMON_INPUT_CLASS}),
            'duration_minutes': forms.NumberInput(attrs={'class': COMMON_INPUT_CLASS}),
            'lecture_type': forms.Select(attrs={'class': COMMON_SELECT_CLASS}),
            'is_preview': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }


class BaseSectionFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        
        # Check if at least one section exists and is not marked for deletion
        valid_forms = [
            form for form in self.forms 
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
        ]
        
        if not valid_forms:
            raise ValidationError("You must add at least one section.")


class BaseLectureFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        
        # Check if at least one lecture exists and is not marked for deletion
        valid_forms = [
            form for form in self.forms 
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
        ]
        
        if not valid_forms:
            raise ValidationError("Each section needs at least one lecture.")


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


class InstructorRequestForm(forms.ModelForm):
    class Meta:
        model = InstructorRequest
        fields = ['motivation', 'qualifications']
        widgets = {
            'motivation': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Explain why you want to become an instructor...'
            }),
            'qualifications': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Describe your qualifications or experience...'
            }),
        }
        labels = {
            'motivation': 'Your Motivation',
            'qualifications': 'Your Qualifications'
        }
        help_texts = {
            'motivation': 'Tell us why you want to teach on our platform',
            'qualifications': 'List any relevant education, experience, or skills'
        }

    def clean(self):
        cleaned_data = super().clean()
        # Add any custom validation here if needed
        return cleaned_data
