# core/urls.py
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("check-cloudinary/", views.check_cloudinary, name="check_cloudinary"),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('courses/<int:course_id>/lesson/<int:lesson_id>/', views.lesson_view, name='lesson_view'),
    path('recommendations/', views.stock_recommendations, name='stock_recommendations'),
    path('news/', views.news, name='news'),
    path('referral/', views.referral_view, name='referral'),
    # ADD THESE NEW ROUTES:
    path('profile/', views.profile_view, name='profile'),
    path('search/', views.search, name='search'),
]