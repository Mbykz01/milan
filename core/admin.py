# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django import forms
from .models import *

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'subscription_tier', 'referral_credits', 'referral_code', 'is_active', 'date_joined')
    list_filter = ('role', 'subscription_tier', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name', 'referral_code')
    readonly_fields = ('date_joined', 'last_login', 'referral_code', 'profile_picture_preview')
    list_per_page = 50
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone', 'profile_picture', 'profile_picture_preview', 'subscription_tier', 'subscription_expiry', 'referral_credits', 'referral_code')
        }),
    )
    
    actions = ['make_premium', 'make_free', 'make_instructor']
    
    def make_premium(self, request, queryset):
        updated = queryset.update(subscription_tier='premium')
        self.message_user(request, f'{updated} users marked as Premium.')
    make_premium.short_description = "Mark selected users as Premium"
    
    def make_free(self, request, queryset):
        updated = queryset.update(subscription_tier='free')
        self.message_user(request, f'{updated} users marked as Free.')
    make_free.short_description = "Mark selected users as Free"
    
    def make_instructor(self, request, queryset):
        updated = queryset.update(role='instructor')
        self.message_user(request, f'{updated} users converted to Instructor.')
    make_instructor.short_description = "Mark selected users as Instructor"
    
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 50%;" />',
                obj.profile_picture_url
            )
        return "No profile picture"
    profile_picture_preview.short_description = 'Profile Picture Preview'

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_count', 'icon')
    search_fields = ('name', 'description')
    list_per_page = 20
    
    def course_count(self, obj):
        return obj.course_set.count()
    course_count.short_description = 'Courses'

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure only instructors are shown
        self.fields['instructor'].queryset = CustomUser.objects.filter(role='instructor').order_by('username')
        # Ensure categories are ordered
        self.fields['category'].queryset = CourseCategory.objects.all().order_by('name')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseForm
    list_display = ('title', 'instructor', 'category', 'level', 'price', 'duration_hours', 'lesson_count', 'is_active', 'created_at', 'thumbnail_preview')
    list_filter = ('category', 'level', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')
    list_editable = ('price', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'thumbnail_preview')
    list_per_page = 20
    
    # Enhanced foreign key handling
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "instructor":
            kwargs["queryset"] = CustomUser.objects.filter(role='instructor').order_by('username')
            if not kwargs["queryset"].exists():
                self.message_user(request, "⚠️ No users with instructor role found. Please create instructors first.", level='WARNING')
        elif db_field.name == "category":
            kwargs["queryset"] = CourseCategory.objects.all().order_by('name')
            if not kwargs["queryset"].exists():
                self.message_user(request, "⚠️ No course categories found. Please create categories first.", level='WARNING')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # Enhanced choice field handling
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "level":
            kwargs['choices'] = db_field.choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)
    
    # Ensure the form works correctly
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['instructor'].label_from_instance = lambda obj: f"{obj.username} ({obj.get_role_display()})"
        return form
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'instructor', 'category', 'level')
        }),
        ('Media & Pricing', {
            'fields': ('thumbnail', 'thumbnail_preview', 'price', 'duration_hours')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="100" height="60" style="object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail_url
            )
        return "No thumbnail"
    thumbnail_preview.short_description = 'Thumbnail Preview'
    
    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Lessons'
    
    def delete_queryset(self, request, queryset):
        for course in queryset:
            course.delete()

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'content_type', 'order', 'duration_minutes', 'is_preview', 'created_at')
    list_filter = ('course', 'content_type', 'is_preview', 'created_at')
    search_fields = ('title', 'course__title', 'description')
    list_editable = ('order', 'duration_minutes', 'is_preview')
    readonly_fields = ('created_at', 'content_preview')
    list_per_page = 30
    
    autocomplete_fields = ['course']
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "content_type":
            kwargs['choices'] = db_field.choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'content_type', 'description', 'order', 'duration_minutes')
        }),
        ('Video Content', {
            'fields': ('video_file', 'video_url'),
            'classes': ('collapse',)
        }),
        ('Image Content', {
            'fields': ('image_content',),
            'classes': ('collapse',)
        }),
        ('PDF Content', {
            'fields': ('pdf_file',),
            'classes': ('collapse',)
        }),
        ('Text Content', {
            'fields': ('text_content',),
            'classes': ('collapse',)
        }),
        ('Preview & Status', {
            'fields': ('content_preview', 'is_preview')
        }),
    )
    
    def content_preview(self, obj):
        if obj.content_type == 'video' and obj.video_file:
            return format_html(
                '<video width="300" controls><source src="{}" type="video/mp4">Your browser does not support the video tag.</video>',
                obj.video_file_url
            )
        elif obj.content_type == 'video' and obj.video_url:
            return format_html('<a href="{}" target="_blank">Watch External Video</a>', obj.video_url)
        elif obj.content_type == 'image' and obj.image_content:
            return format_html(
                '<img src="{}" width="300" style="max-height: 200px; object-fit: contain;" />',
                obj.image_content_url
            )
        elif obj.content_type == 'pdf' and obj.pdf_file:
            return format_html('<a href="{}" target="_blank">View PDF Document</a>', obj.pdf_file.url)
        elif obj.content_type == 'text' and obj.text_content:
            preview = obj.text_content[:100] + '...' if len(obj.text_content) > 100 else obj.text_content
            return format_html('<div style="max-width: 300px; padding: 10px; border: 1px solid #ddd; background: #f9f9f9;">{}</div>', preview)
        return "No content available"
    content_preview.short_description = 'Content Preview'
    
    def delete_queryset(self, request, queryset):
        for lesson in queryset:
            lesson.delete()

@admin.register(StockRecommendation)
class StockRecommendationAdmin(admin.ModelAdmin):
    list_display = ('stock_symbol', 'company_name', 'recommendation', 'current_price', 'target_price', 'risk_level', 'published_date', 'is_active')
    list_filter = ('recommendation', 'risk_level', 'is_active', 'published_date')
    search_fields = ('stock_symbol', 'company_name', 'analysis')
    list_editable = ('recommendation', 'current_price', 'target_price', 'risk_level', 'is_active')
    readonly_fields = ('published_date',)
    list_per_page = 20
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name in ["recommendation", "risk_level"]:
            kwargs['choices'] = db_field.choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)
    
    fieldsets = (
        ('Stock Information', {
            'fields': ('stock_symbol', 'company_name')
        }),
        ('Recommendation Details', {
            'fields': ('recommendation', 'current_price', 'target_price', 'risk_level', 'analysis')
        }),
        ('Timing', {
            'fields': ('published_date', 'expiry_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_date', 'is_active', 'image_preview', 'created_at')
    list_filter = ('source', 'is_active', 'published_date', 'created_at')
    search_fields = ('title', 'content', 'summary', 'tags')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'image_preview')
    list_per_page = 30
    
    fieldsets = (
        ('Article Content', {
            'fields': ('title', 'content', 'summary')
        }),
        ('Source & Media', {
            'fields': ('source', 'image_url', 'image_file', 'image_preview', 'tags')
        }),
        ('Publication', {
            'fields': ('published_date', 'is_active')
        }),
    )
    
    def image_preview(self, obj):
        if obj.image_file:
            return format_html(
                '<img src="{}" width="100" height="60" style="object-fit: cover; border-radius: 4px;" />',
                obj.image_file_url
            )
        elif obj.image_url:
            return format_html(
                '<img src="{}" width="100" height="60" style="object-fit: cover; border-radius: 4px;" />',
                obj.image_url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'
    
    def delete_queryset(self, request, queryset):
        for news in queryset:
            news.delete()

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'completed', 'progress_display')
    list_filter = ('completed', 'enrolled_at', 'course')
    search_fields = ('user__username', 'course__title')
    readonly_fields = ('enrolled_at',)
    list_per_page = 50
    
    autocomplete_fields = ['user', 'course']
    
    def progress_display(self, obj):
        return f"{obj.progress}%"
    progress_display.short_description = 'Progress'

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred_user', 'credit_amount', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('referrer__username', 'referred_user__username')
    list_per_page = 50
    
    autocomplete_fields = ['referrer', 'referred_user']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'subscription_type', 'payment_status', 'payment_date')
    list_filter = ('payment_status', 'subscription_type', 'payment_date')
    search_fields = ('user__username', 'transaction_id')
    readonly_fields = ('payment_date',)
    list_per_page = 50
    
    autocomplete_fields = ['user', 'course']
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name in ["subscription_type", "payment_status"]:
            kwargs['choices'] = db_field.choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)

admin.site.site_header = "📈 StockLearn Administration"
admin.site.site_title = "StockLearn Admin Portal"
admin.site.index_title = "Welcome to StockLearn - Complete Management Portal"