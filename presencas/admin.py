from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_group', 'date', 'is_present']
    list_filter = ['is_present', 'class_group', 'date']
    search_fields = ['student__name']
    date_hierarchy = 'date'
