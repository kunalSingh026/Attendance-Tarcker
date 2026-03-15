from django.contrib import admin
from .models import Course, AttendanceRecord

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'total_classes_held')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('course', 'date', 'status', 'user')
    search_fields = ('course__name', 'user__username')
    list_filter = ('status', 'date', 'course')
    date_hierarchy = 'date'