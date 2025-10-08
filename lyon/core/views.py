# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
import os
from .models import *
from .forms import CustomUserCreationForm, ProfileUpdateForm

def home(request):
    courses = Course.objects.filter(is_active=True).order_by('-created_at')[:6]
    categories = CourseCategory.objects.all()
    news_articles = NewsArticle.objects.filter(is_active=True).order_by('-published_date')[:3]
    recommendations = StockRecommendation.objects.filter(is_active=True).order_by('-published_date')[:2]
    
    context = {
        'courses': courses,
        'categories': categories,
        'news_articles': news_articles,
        'recommendations': recommendations,
    }
    return render(request, 'core/home.html', context)  # Fixed template path

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Handle referral logic - BOTH URL parameter AND form field
            referral_source = None
            
            # Check URL parameter first (from referral link)
            referral_code_from_url = request.GET.get('ref')
            if referral_code_from_url:
                referral_source = referral_code_from_url
            
            # Check form field (manual entry)
            referral_code_from_form = form.cleaned_data.get('referral_code')
            if referral_code_from_form and not referral_source:
                referral_source = referral_code_from_form
            
            # Process referral if exists
            if referral_source:
                try:
                    referrer = CustomUser.objects.get(referral_code=referral_source)
                    # Create referral record
                    Referral.objects.create(
                        referrer=referrer,
                        referred_user=user,
                        credit_amount=50.00
                    )
                    # Add credits to both users
                    referrer.referral_credits += 50.00
                    referrer.save()
                    
                    user.referral_credits += 25.00  # Bonus for new user too
                    user.save()
                    
                    messages.success(request, f'Referral bonus applied! You received $25 credits.')
                except CustomUser.DoesNotExist:
                    messages.warning(request, 'Invalid referral code. Account created without referral bonus.')
            
            # Auto-login after signup
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome to Lyon, {user.username}!')
            return redirect('core:dashboard')  # Fixed redirect
    else:
        # Pre-fill referral code from URL if provided
        initial_data = {}
        referral_code = request.GET.get('ref')
        if referral_code:
            initial_data['referral_code'] = referral_code
            # Verify the referral code exists
            try:
                referrer = CustomUser.objects.get(referral_code=referral_code)
                messages.info(request, f'You are signing up with {referrer.username}\'s referral link!')
            except CustomUser.DoesNotExist:
                messages.warning(request, 'Invalid referral link, but you can still sign up.')
        
        form = CustomUserCreationForm(initial=initial_data)
    
    return render(request, 'core/signup.html', {'form': form})  # Fixed template path

def login_view(request):
    # Capture next param (if user was redirected from @login_required page)
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            # Redirect to next page if exists, otherwise dashboard
            if next_url:
                return redirect(next_url)
            return redirect('core:dashboard')  # Fixed redirect
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'core/login.html', {'next': next_url})  # Fixed template path

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')  # Fixed redirect

@login_required
def dashboard(request):
    user_enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    in_progress_courses = user_enrollments.filter(completed=False)
    completed_courses = user_enrollments.filter(completed=True)

    # Get user's referral stats
    user_referrals = Referral.objects.filter(referrer=request.user)
    referral_url = f"{request.build_absolute_uri('/signup/')}?ref={request.user.referral_code}"

    if request.user.subscription_tier == 'premium':
        recommendations = StockRecommendation.objects.filter(is_active=True).order_by('-published_date')[:5]
        news_articles = NewsArticle.objects.filter(is_active=True).order_by('-published_date')[:5]
    else:
        recommendations = StockRecommendation.objects.filter(is_active=True).order_by('-published_date')[:2]
        news_articles = NewsArticle.objects.filter(is_active=True).order_by('-published_date')[:3]

    context = {
        'in_progress_courses': in_progress_courses,
        'completed_courses': completed_courses,
        'recommendations': recommendations,
        'news_articles': news_articles,
        'user_referrals': user_referrals,
        'referral_url': referral_url,
    }
    return render(request, 'core/dashboard.html', context)  # Fixed template path

@login_required
def course_list(request):
    courses = Course.objects.filter(is_active=True)
    category_id = request.GET.get('category')
    level = request.GET.get('level')
    search_query = request.GET.get('search')

    if category_id:
        courses = courses.filter(category_id=category_id)
    if level:
        courses = courses.filter(level=level)
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(instructor__icontains=search_query)
        )

    categories = CourseCategory.objects.all()
    return render(request, 'core/course_list.html', {
        'courses': courses,
        'categories': categories,
    })  # Fixed template path

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)
    lessons = course.lessons.all().order_by('order')
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

    # Safe check for subscription_tier
    user_subscription = getattr(request.user, 'subscription_tier', 'free')
    can_access = (is_enrolled or user_subscription == 'premium' or course.price == 0)

    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'can_access': can_access,
    }
    return render(request, 'core/course_detail.html', context)  # Fixed template path

@login_required
def lesson_view(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    user_subscription = getattr(request.user, 'subscription_tier', 'free')
    
    if not (is_enrolled or user_subscription == 'premium' or course.price == 0):
        messages.error(request, 'You need to enroll in this course to access the lessons.')
        return redirect('core:course_detail', course_id=course_id)  # Fixed redirect

    lessons = course.lessons.all().order_by('order')
    current_lesson_index = list(lessons).index(lesson)
    next_lesson = lessons[current_lesson_index + 1] if current_lesson_index + 1 < len(lessons) else None
    previous_lesson = lessons[current_lesson_index - 1] if current_lesson_index - 1 >= 0 else None

    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    total_lessons = lessons.count()
    completed_lessons = min(current_lesson_index + 1, total_lessons)
    enrollment.progress = (completed_lessons / total_lessons) * 100
    if enrollment.progress == 100:
        enrollment.completed = True
    enrollment.save()

    # Create a string for inline width
    progress_width = f"{enrollment.progress:.0f}%"

    context = {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
        'next_lesson': next_lesson,
        'previous_lesson': previous_lesson,
        'progress': enrollment.progress,
        'progress_width': progress_width,
    }
    return render(request, 'core/lesson.html', context)  # Fixed template path

@login_required
def stock_recommendations(request):
    recommendations = StockRecommendation.objects.filter(is_active=True).order_by('-published_date')

    if request.user.subscription_tier != 'premium':
        recommendations = recommendations[:3]
        messages.info(request, 'Upgrade to premium for full access to all stock recommendations.')

    return render(request, 'core/stock_recommendations.html', {
        'recommendations': recommendations,
    })  # Fixed template path

@login_required
def news(request):
    news_articles = NewsArticle.objects.filter(is_active=True).order_by('-published_date')

    if request.user.subscription_tier != 'premium':
        news_articles = news_articles[:5]
        messages.info(request, 'Upgrade to premium for unlimited access to daily market news.')

    return render(request, 'core/news.html', {
        'news_articles': news_articles,
    })  # Fixed template path

@login_required
def referral_view(request):
    user_referrals = Referral.objects.filter(referrer=request.user)
    referral_url = f"{request.build_absolute_uri('/signup/')}?ref={request.user.referral_code}"

    # Calculate total earned from referrals
    total_earned = sum([referral.credit_amount for referral in user_referrals])

    context = {
        'user_referrals': user_referrals,
        'referral_url': referral_url,
        'available_credits': request.user.referral_credits,
        'total_earned': total_earned,
        'referral_count': user_referrals.count(),
    }
    return render(request, 'core/referral.html', context)  # Fixed template path

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('core:course_detail', course_id=course_id)  # Fixed redirect

    # Check if course is free, user has premium, or can use credits
    if course.price == 0 or request.user.subscription_tier == 'premium':
        Enrollment.objects.create(user=request.user, course=course)
        messages.success(request, f'Successfully enrolled in {course.title}')
        return redirect('core:course_detail', course_id=course_id)  # Fixed redirect

    # Check if user has enough referral credits
    if request.user.referral_credits >= course.price:
        request.user.referral_credits -= course.price
        request.user.save()
        Enrollment.objects.create(user=request.user, course=course)
        messages.success(request, f'Enrolled in {course.title} using referral credits!')
        return redirect('core:course_detail', course_id=course_id)  # Fixed redirect
    else:
        messages.error(request, f'Insufficient credits. You need ${course.price} but have ${request.user.referral_credits:.2f}.')
        return redirect('core:course_detail', course_id=course_id)  # Fixed redirect

# NEW VIEWS FOR PROFILE MANAGEMENT
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('core:profile')  # Fixed redirect
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'core/profile.html', {'form': form})  # Fixed template path

# Search functionality
@login_required
def search(request):
    query = request.GET.get('q', '')
    if query:
        courses = Course.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(instructor__icontains=query)
        ).filter(is_active=True)
        
        news_articles = NewsArticle.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(tags__icontains=query)
        ).filter(is_active=True)
        
        recommendations = StockRecommendation.objects.filter(
            Q(stock_symbol__icontains=query) |
            Q(company_name__icontains=query) |
            Q(analysis__icontains=query)
        ).filter(is_active=True)
    else:
        courses = Course.objects.none()
        news_articles = NewsArticle.objects.none()
        recommendations = StockRecommendation.objects.none()

    context = {
        'query': query,
        'courses': courses,
        'news_articles': news_articles,
        'recommendations': recommendations,
    }
    return render(request, 'core/search_results.html', context)  # Fixed template path

# API endpoint to check Cloudinary (for debugging - remove in production if needed)
def check_cloudinary(request):
    if not request.user.is_superuser:  # Only allow admins
        return HttpResponse("Unauthorized", status=403)
        
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
    api_key = os.environ.get("CLOUDINARY_API_KEY")
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")

    if cloud_name and api_key and api_secret:
        return HttpResponse(f"✅ Cloudinary variables detected!<br>"
                            f"CLOUD_NAME: {cloud_name}<br>"
                            f"API_KEY: {api_key}<br>"
                            f"API_SECRET: {api_secret[:4]}********")
    else:
        return HttpResponse("❌ Missing Cloudinary environment variables!")