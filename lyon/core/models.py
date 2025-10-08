# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField


class CustomUser(AbstractUser):
    USER_ROLES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default='student')
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = CloudinaryField('image', folder='core/profiles/', blank=True, null=True)
    subscription_tier = models.CharField(
        max_length=20, 
        choices=[('free', 'Free'), ('premium', 'Premium')], 
        default='free'
    )
    subscription_expiry = models.DateTimeField(null=True, blank=True)
    referral_credits = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    referral_code = models.CharField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            # Generate a unique referral code based on username
            base_code = self.username.lower().replace(' ', '')[:8]
            self.referral_code = base_code
            counter = 1
            while CustomUser.objects.filter(referral_code=self.referral_code).exists():
                self.referral_code = f"{base_code}{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None


class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='📚')
    
    def __str__(self):
        return self.name


class Course(models.Model):
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=200, blank=True, null=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    thumbnail = CloudinaryField('image', folder='core/course_thumbnails/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_hours = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return None


class Lesson(models.Model):
    CONTENT_TYPES = (
        ('video', 'Video Lesson'),
        ('image', 'Image Content'),
        ('pdf', 'PDF Document'),
        ('text', 'Text Content'),
        ('quiz', 'Quiz'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='video')
    description = models.TextField(blank=True)
    
    # For video lessons - using Cloudinary for video storage
    video_file = CloudinaryField('video', resource_type='video', folder='core/course_videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    
    # For image/content lessons - using Cloudinary for images
    image_content = CloudinaryField('image', folder='core/lesson_images/', blank=True, null=True)
    
    # PDF files remain as FileField since Cloudinary might not be ideal for PDFs
    # or you can use CloudinaryField with resource_type='raw' for PDFs
    pdf_file = models.FileField(upload_to='core/course_pdfs/', blank=True, null=True)
    
    text_content = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField()
    is_preview = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def has_video(self):
        return bool(self.video_file or self.video_url)
    
    @property
    def has_image(self):
        return bool(self.image_content)
    
    @property
    def has_pdf(self):
        return bool(self.pdf_file)
    
    @property
    def has_text(self):
        return bool(self.text_content)
    
    @property
    def video_file_url(self):
        if self.video_file:
            return self.video_file.url
        return None
    
    @property
    def image_content_url(self):
        if self.image_content:
            return self.image_content.url
        return None


class Enrollment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    progress = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        unique_together = ['user', 'course']


class StockRecommendation(models.Model):
    stock_symbol = models.CharField(max_length=10)
    company_name = models.CharField(max_length=200)
    recommendation = models.CharField(
        max_length=20,
        choices=[('buy', 'Buy'), ('hold', 'Hold'), ('sell', 'Sell')]
    )
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    analysis = models.TextField()
    risk_level = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    )
    published_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.stock_symbol} - {self.recommendation}"


class NewsArticle(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    summary = models.TextField(blank=True)
    source = models.CharField(max_length=100)
    published_date = models.DateTimeField()
    image_url = models.URLField(blank=True)
    image_file = CloudinaryField('image', folder='core/news_images/', blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    @property
    def image_file_url(self):
        if self.image_file:
            return self.image_file.url
        return self.image_url


class Referral(models.Model):
    referrer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='referred_by')
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.referrer.username} -> {self.referred_user.username}"


class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    subscription_type = models.CharField(max_length=20, choices=[('course', 'Course'), ('subscription', 'Subscription')])
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')],
        default='pending'
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.payment_status}"