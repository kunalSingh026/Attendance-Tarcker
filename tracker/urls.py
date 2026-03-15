from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('courses/', views.manage_courses, name='manage_courses'),
    path('track/', views.track_attendance, name='track_attendance'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    # NEW PATHS FOR PROFILE MANAGEMENT
    path('dashboard/upload_pic/', views.upload_profile_pic, name='upload_profile_pic'),
    path('dashboard/update_avatar/', views.update_avatar, name='update_avatar'),
    # path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
]

