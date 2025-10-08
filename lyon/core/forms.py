# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Course, Lesson, StockRecommendation, NewsArticle

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email Address",
        help_text="We'll never share your email with anyone else.",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        label="Phone Number (Optional)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'})
    )
    referral_code = forms.CharField(
        max_length=100, 
        required=False, 
        label="Referral Code (Optional)",
        help_text="Enter a friend's referral code to get bonus credits",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter referral code'})
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "phone",
            "password1",
            "password2",
            "referral_code",
        )
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field_name != 'referral_code':  # referral_code already has class
                field.widget.attrs['class'] = 'form-control'


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title", "description", "category", "level", "thumbnail",
            "price", "duration_hours"
        ]
        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course title'}),
            "description": forms.Textarea(attrs={"rows": 4, 'class': 'form-control', 'placeholder': 'Enter course description'}),
            "category": forms.Select(attrs={'class': 'form-control'}),
            "level": forms.Select(attrs={'class': 'form-control'}),
            "price": forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            "duration_hours": forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make thumbnail field optional with better styling
        self.fields['thumbnail'].required = False
        self.fields['thumbnail'].widget.attrs['class'] = 'form-control'


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            "course", "title", "content_type", "description", 
            "video_file", "video_url", "image_content", "pdf_file",
            "text_content", "duration_minutes", "order", "is_preview"
        ]
        widgets = {
            "course": forms.Select(attrs={'class': 'form-control'}),
            "title": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter lesson title'}),
            "content_type": forms.Select(attrs={'class': 'form-control'}),
            "description": forms.Textarea(attrs={"rows": 4, 'class': 'form-control', 'placeholder': 'Enter lesson description'}),
            "video_url": forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/video'}),
            "duration_minutes": forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            "order": forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            "text_content": forms.Textarea(attrs={"rows": 10, 'class': 'form-control', 'placeholder': 'Enter text content here...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to file fields
        self.fields['video_file'].widget.attrs['class'] = 'form-control'
        self.fields['image_content'].widget.attrs['class'] = 'form-control'
        self.fields['pdf_file'].widget.attrs['class'] = 'form-control'
        
        # Make file fields optional
        self.fields['video_file'].required = False
        self.fields['image_content'].required = False
        self.fields['pdf_file'].required = False
        self.fields['video_url'].required = False


class StockRecommendationForm(forms.ModelForm):
    class Meta:
        model = StockRecommendation
        fields = [
            "stock_symbol", "company_name", "recommendation",
            "target_price", "current_price", "analysis",
            "risk_level", "expiry_date"
        ]
        widgets = {
            "stock_symbol": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., AAPL'}),
            "company_name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company name'}),
            "recommendation": forms.Select(attrs={'class': 'form-control'}),
            "target_price": forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            "current_price": forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            "analysis": forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Enter detailed analysis...'}),
            "risk_level": forms.Select(attrs={'class': 'form-control'}),
            "expiry_date": forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class NewsArticleForm(forms.ModelForm):
    class Meta:
        model = NewsArticle
        fields = [
            "title", "content", "summary", "source", "published_date",
            "image_url", "image_file", "tags"
        ]
        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter article title'}),
            "content": forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Enter article content...'}),
            "summary": forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter brief summary...'}),
            "source": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter news source'}),
            "published_date": forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            "image_url": forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/image.jpg'}),
            "tags": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'tag1, tag2, tag3'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap class to image file field
        self.fields['image_file'].widget.attrs['class'] = 'form-control'
        
        # Make image fields optional
        self.fields['image_file'].required = False
        self.fields['image_url'].required = False


# Optional: Profile update form for users
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }