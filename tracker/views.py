from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from datetime import date, timedelta, datetime
from django.utils import timezone
from django.views.decorators.http import require_POST # <--- NEW/CONFIRMED IMPORT
import calendar
from django.db import IntegrityError
from .models import Course, AttendanceRecord, Profile
from django.db.models import Count, Sum, Q
import json # <--- CONFIRMED IMPORT

# -----------------------------
# Helper Functions
# -----------------------------

def get_current_week():
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def calculate_attendance_stats(user, courses, start_date=None, end_date=None):
    """ 
    Helper function to calculate attendance stats for a given time range. 
    Uses 'status' field (1=Present, 2=Absent) and EXCLUDES status=3 (Holiday/Cancelled).
    """
    stats = []
    
    # Define statuses for PRESENT and ABSENT (classes that actually happened)
    CLASS_HELD_STATUSES = [1, 2] 
    
    for course in courses:
        # Filter records for the specific course and date range
        records = AttendanceRecord.objects.filter(course=course)
        if start_date:
            records = records.filter(date__gte=start_date)
        if end_date:
            records = records.filter(date__lte=end_date)

        # Filter records to only include classes that were actually held (status 1 or 2)
        held_classes_records = records.filter(status__in=CLASS_HELD_STATUSES)
        
        # Calculate counts
        total_classes = held_classes_records.count()
        present_count = held_classes_records.filter(status=1).count()
        absent_count = held_classes_records.filter(status=2).count()
        
        # Calculate percentage
        percentage = round((present_count / total_classes) * 100, 1) if total_classes > 0 else 100.0

        stats.append({
            'name': course.name,
            'course__name': course.name,
            'total_classes': total_classes, # Total classes HELD in this range
            'total': total_classes,
            'present_count': present_count,
            'present': present_count,
            'absent_count': absent_count,
            'absent': absent_count,
            'percentage': percentage,
            'id': course.id,
        })
    return stats

def mark_attendance_for_date(request, course_id, status_int, record_date):
    """
    Core logic to create or update an attendance record for a specific date.
    Accepts the request object for accessing user and sending messages.
    """
    try:
        # **FIXED**: Ensures request.user is used for fetching the course
        course = Course.objects.get(id=course_id, user=request.user) 
        user = request.user
        
        # Convert status integer to a descriptive string for messages
        status_name = {1: "Present", 2: "Absent", 3: "Holiday/Cancelled"}.get(status_int, "Unknown")

        # Get or create the attendance record
        record, created = AttendanceRecord.objects.get_or_create(
            user=user,
            course=course,
            date=record_date,
            defaults={'status': status_int}
        )
        
        # Determine if the record should count toward total_classes_held
        counts_as_class = status_int in [1, 2] # Only Present or Absent counts

        if created:
            # If a new record was created, increment total_classes_held only if it counts as a held class
            if counts_as_class:
                course.total_classes_held += 1
                course.save()
            
            date_str = record_date.strftime("%b %d, %Y")
            # **FIXED**: Pass 'request' object to messages
            messages.success(request, f'Attendance marked: {course.name} set as {status_name} for {date_str}.')
            
        else:
            # If the record already existed, handle update logic
            old_status = record.status
            
            if old_status != status_int:
                
                # Check if the total_classes_held needs adjustment
                old_counts = old_status in [1, 2]
                new_counts = status_int in [1, 2]
                
                if old_counts and not new_counts:
                    # Changing from Present/Absent to Holiday -> DECREMENT total_classes_held
                    course.total_classes_held = max(0, course.total_classes_held - 1)
                    course.save()
                elif not old_counts and new_counts:
                    # Changing from Holiday to Present/Absent -> INCREMENT total_classes_held
                    course.total_classes_held += 1
                    course.save()

                # Perform the record update
                record.status = status_int
                record.save()
                
                date_str = record_date.strftime("%b %d, %Y")
                # **FIXED**: Pass 'request' object to messages
                messages.info(request, f'Attendance updated: {course.name} changed to {status_name} for {date_str}.')
            else:
                date_str = record_date.strftime("%b %d, %Y")
                # **FIXED**: Pass 'request' object to messages
                messages.warning(request, f'Attendance for {course.name} is already marked as {status_name} for {date_str}.')

        return True

    except Course.DoesNotExist:
        # **FIXED**: Pass 'request' object to messages
        messages.error(request, 'Invalid course selected.')
    except Exception as e:
        # **FIXED**: Pass 'request' object to messages
        messages.error(request, f'An unexpected error occurred: {e}')
        
    return False

# -----------------------------
# Authentication & Basic Views
# -----------------------------
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    percentage = None
    if request.method == "POST":
        try:
            total_classes = int(request.POST.get("total_classes", 0))
            attended_classes = int(request.POST.get("attended_classes", 0))
        except ValueError:
            messages.error(request, "Please enter valid numbers.")
            return redirect('home')

        if total_classes > 0:
            percentage = round((attended_classes / total_classes) * 100, 2)
        else:
            percentage = 0

    return render(request, "tracker/home.html", {"percentage": percentage})

def signup_view(request):
    if request.method == 'POST':
        # Safely access POST data
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Validation checks
        if not (username and password and password2):
            messages.error(request, "Please fill in all required fields.")
            return redirect('signup')

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            # --- NEW: Create Profile object immediately ---
            Profile.objects.create(user=user)
            # ---------------------------------------------
            messages.success(request, "Account created. You can log in now.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error creating user: {e}")
            return redirect('signup')

    return render(request, 'tracker/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')

    return render(request, 'tracker/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def calendar_view(request):
    user = request.user
    
    all_records = AttendanceRecord.objects.filter(user=user).order_by('date')
    CLASS_HELD_STATUSES = [1, 2] 

    daily_summary = all_records.filter(status__in=CLASS_HELD_STATUSES).values('date').annotate(
        total_present=Count('id', filter=Q(status=1)),
        total_records=Count('id')
    ).order_by('date')

    calendar_events = []
    
    for summary in daily_summary:
        record_date = summary['date']
        total_present = summary['total_present']
        total_records = summary['total_records']
        
        if total_records == 0:
            status_class = 'neutral'
            status_text = 'No Classes'
            percentage = 0.0
        else:
            percentage = (total_present / total_records) * 100
            if percentage >= 75:
                status_class = 'present-safe'
                status_text = 'High Attendance'
            elif percentage >= 50:
                status_class = 'present-warning'
                status_text = 'Medium Attendance'
            else:
                status_class = 'absent-danger'
                status_text = 'Low Attendance'

        details = all_records.filter(date=record_date).values('course__name', 'status')
        
        calendar_events.append({
            'date': record_date.isoformat(),
            'title': f"{total_present}/{total_records} classes present",
            'percentage': round(percentage, 1),
            'className': status_class,
            'status_text': status_text,
            'details': list(details),
        })

    
    calendar_events_json = json.dumps(calendar_events)

    context = {
        'calendar_events_json': calendar_events_json, 
        'calendar_events': calendar_events,
    }
    return render(request, 'tracker/calendar.html', context)


# -----------------------------
# Course Management 
# -----------------------------
@login_required
def manage_courses(request):
    user = request.user
    
    if request.method == 'POST':
        course_name = request.POST.get('course_name', '').strip()
        
        if course_name:
            try:
                Course.objects.create(
                    user=user, 
                    name=course_name,
                )
                messages.success(request, f'Course "{course_name}" added successfully!')
            except IntegrityError:
                messages.error(request, f'You already have a course named "{course_name}".')
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')
        else:
            messages.warning(request, 'Course name cannot be empty.')
            
        return redirect('manage_courses')

    user_courses = Course.objects.filter(user=user).order_by('name')

    context = {
        'courses': user_courses,
    }
    return render(request, 'tracker/manage_courses.html', context)


@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id, user=request.user)
    
    if request.method == 'POST':
        course_name = course.name
        course.delete()
        messages.success(request, f'Course "{course_name}" and all attendance records deleted.')
        
    return redirect('manage_courses')


# -----------------------------
# Attendance Tracking 
# -----------------------------

@login_required
def track_attendance(request):
    """
    Handles the daily/historical attendance marking interface and submission.
    """
    user = request.user
    
    # Get the date from the request or default to today
    selected_date_str = request.GET.get('date', timezone.now().date().isoformat())
    
    try:
        # Convert string date to Python date object
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = timezone.now().date()
        messages.error(request, "Invalid date provided. Showing today's attendance.")

    # 1. Handle POST submission (marking attendance for the selected date)
    if request.method == 'POST':
        form_date_str = request.POST.get('record_date')
        
        try:
            record_date = datetime.strptime(form_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format submitted.")
            return redirect('track_attendance')

        course_id = request.POST.get('course_id')
        
        # Prevent future date attendance
        if record_date > timezone.now().date():
            messages.error(request, "You cannot mark attendance for a future date.")
            return redirect(f"{request.path}?date={record_date.isoformat()}")

        # Status now comes as an integer string ('1', '2', or '3')
        status_str = request.POST.get('status')
        try:
            status_int = int(status_str)
        except (ValueError, TypeError):
            messages.error(request, "Invalid attendance status submitted.")
            return redirect(f"{request.path}?date={record_date.isoformat()}")

        mark_attendance_for_date(request, course_id, status_int, record_date) 
        return redirect(f"{request.path}?date={record_date.isoformat()}")

    # 2. Handle GET request (displaying the form)
    
    user_courses = Course.objects.filter(user=user).order_by('name')
    
    if not user_courses.exists():
        messages.info(request, "Please add courses before tracking attendance.")
        return redirect('manage_courses')
        
    # Check status for each course for the selected date
    attendance_data = []
    
    for course in user_courses:
        record = AttendanceRecord.objects.filter(course=course, date=selected_date).first()
        
        if record:
            # Use status integer to determine marked status text
            if record.status == 1:
                status_marked = "Present"
            elif record.status == 2:
                status_marked = "Absent"
            else: # status == 3
                status_marked = "Holiday/Cancelled"

            is_marked = True
            status_val = record.status
        else:
            status_marked = "Not Marked"
            is_marked = False
            status_val = None
            
        attendance_data.append({
            'course': course,
            'status_marked': status_marked,
            'is_marked': is_marked,
            'status': status_val,
        })
        
    context = {
        'attendance_data': attendance_data,
        'selected_date': selected_date,
        'is_today': selected_date == timezone.now().date(),
        'is_future': selected_date > timezone.now().date(),
        'today': timezone.now().date(),
    }
    return render(request, 'tracker/track_attendance.html', context)

# -----------------------------
# Dashboard View (UPDATED)
# -----------------------------

@login_required
def dashboard_view(request):
    user = request.user
    
    # --- NEW 1: Ensure Profile exists and fetch it ---
    # This ensures the template always has access to 'user_profile'
    user_profile, created = Profile.objects.get_or_create(user=user)
    
    # --- 2. Get User's Courses ---
    user_courses = Course.objects.filter(user=user).order_by('name')
    
    if not user_courses.exists():
        messages.warning(request, "Please add courses before viewing the dashboard.")
        return redirect('manage_courses')

    # --- 3. Define Time Ranges ---
    today = timezone.now().date()
    
    # Monthly Range (from the 1st of the current month to today)
    start_of_month = today.replace(day=1)
    
    # Weekly Range (from last Monday to today)
    start_of_week = today - timedelta(days=today.weekday()) 

    # --- 4. Calculate Stats for Different Reports ---
    overall_stats = calculate_attendance_stats(user, user_courses)
    monthly_stats = calculate_attendance_stats(user, user_courses, start_date=start_of_month)
    weekly_stats = calculate_attendance_stats(user, user_courses, start_date=start_of_week)
    
    # --- 5. Calculate Combined Overall Attendance (for the main pie chart) ---
    total_present = sum(s['present_count'] for s in overall_stats)
    total_classes = sum(s['total_classes'] for s in overall_stats)
    total_absent = total_classes - total_present
    
    overall_percentage = round((total_present / total_classes) * 100, 1) if total_classes > 0 else 100.0
    
    # Data structure for the main pie chart (for the frontend)
    main_chart_data = {
        'present': total_present,
        'absent': total_absent,
    }

    context = {
        'overall_percentage': overall_percentage,
        'main_chart_data_json': json.dumps(main_chart_data), # Send this as JSON to the template
        'overall_stats': overall_stats,
        'monthly_stats': monthly_stats,
        'weekly_stats': weekly_stats,
        'month_name': today.strftime("%B"),
        # --- NEW 2: Pass the profile object ---
        'user_profile': user_profile, 
    }
    return render(request, 'tracker/dashboard.html', context)

# -----------------------------
# Profile Management (NEW VIEWS)
# -----------------------------

@login_required
@require_POST
def upload_profile_pic(request):
    """Handles the upload of a custom profile picture."""
    try:
        profile = request.user.profile
        
        if 'profile_picture' in request.FILES:
            # Clear old avatar name, delete old profile picture, and save new one
            profile.avatar_name = '' 
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            
            messages.success(request, 'Profile picture uploaded successfully! 📸')
        else:
            messages.error(request, 'No file selected for upload.')
    except Profile.DoesNotExist:
        messages.error(request, 'User profile not found. Please log out and back in.')
    except Exception as e:
        messages.error(request, f'An unexpected error occurred during upload: {e}')
        
    return redirect('dashboard')


@login_required
@require_POST
def update_avatar(request):
    """Handles the selection and saving of an avatar via AJAX/JSON."""
    if request.content_type != 'application/json':
        return JsonResponse({'success': False, 'message': 'Invalid Content-Type.'}, status=400)
        
    try:
        data = json.loads(request.body)
        avatar_name = data.get('avatar_name')
        
        if avatar_name:
            profile = request.user.profile
            
            # 1. Delete the custom picture file (if one exists)
            if profile.profile_picture:
                profile.profile_picture.delete(save=False) # delete file but don't hit DB yet
            
            # 2. Update the avatar name
            profile.avatar_name = avatar_name
            profile.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Avatar updated.',
                # Send the new URL back to update the display immediately
                'new_image_url': profile.get_profile_image_url()
            })
        
        return JsonResponse({'success': False, 'message': 'Avatar name missing.'}, status=400)
    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User profile not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)