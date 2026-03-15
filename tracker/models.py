from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 1. Course Model
# Defines a subject the user is tracking attendance for.
class Course(models.Model):
    # Links the course to a specific user (foreign key to Django's built-in User model)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Name of the course (e.g., "Calculus I", "Web Development")
    name = models.CharField(max_length=100)
    
    # Total number of classes held so far (for initial setup/manual adjustment)
    # Note: This field could also be calculated, but keeping it explicit simplifies the dashboard calculation later.
    total_classes_held = models.IntegerField(default=0) 

    def __str__(self):
        return f"{self.name} (User: {self.user.username})"

    class Meta:
        # Ensures a user cannot create two courses with the exact same name
        unique_together = ('user', 'name',)
        
# 2. Attendance Record Model
# Records the daily status for a specific course.
class AttendanceRecord(models.Model):
    # Links the record to the user (necessary for security and scoping)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Links the record to a specific Course object
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    # The date the attendance was recorded (unique per course to prevent duplicate entries)
    date = models.DateField(default=timezone.now)
    
    # Attendance status: True for present, False for absent
    STATUS_CHOICES = (
        (1, 'Present'),
        (2, 'Absent'),
        (3, 'Holiday/Cancelled'),
    )

    # Attendance status: 1=Present, 2=Absent, 3=Holiday/Cancelled
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.course.name} on {self.date.strftime('%Y-%m-%d')}: {status}"

    class Meta:
        # Ensures a user can only record one attendance status for a given course on a specific date
        unique_together = ('course', 'date',)
        ordering = ['-date'] # Show most recent records first



    # 3. User Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Stores the path for custom uploaded profile picture
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Stores the identifier for a chosen avatar (e.g., 'avatar_1.png')
    avatar_name = models.CharField(max_length=50, default='default_avatar.png') 
    
    # Optional field for additional user info
    student_id = models.CharField(max_length=20, blank=True, null=True) 

    def get_profile_image_url(self):
        """Returns the URL of the profile picture or the default avatar."""
        # Prioritize custom upload
        if self.profile_picture:
            return self.profile_picture.url
        # Fallback to avatar
        # Ensure your static files are served from /static/
        return f'/static/tracker/avatars/{self.avatar_name}' 

    def __str__(self):
        return f"{self.user.username}'s Profile"