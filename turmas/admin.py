from django.contrib import admin
from .models import Instructor, ClassGroup, ClassSchedule, ClassEnrollment


class ScheduleInline(admin.TabularInline):
    model = ClassSchedule
    extra = 1


class EnrollmentInline(admin.TabularInline):
    model = ClassEnrollment
    extra = 0


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'active']
    filter_horizontal = ['modalities']


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'modality', 'instructor', 'max_capacity', 'active']
    list_filter = ['active', 'modality']
    inlines = [ScheduleInline, EnrollmentInline]


@admin.register(ClassEnrollment)
class ClassEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_group', 'enrollment_date', 'active']
    list_filter = ['active', 'class_group']
    search_fields = ['student__name']
