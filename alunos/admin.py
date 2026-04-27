from django.contrib import admin
from .models import Modality, Belt, Student, StudentGraduation


@admin.register(Modality)
class ModalityAdmin(admin.ModelAdmin):
    list_display = ['name', 'active']
    list_filter = ['active']


@admin.register(Belt)
class BeltAdmin(admin.ModelAdmin):
    list_display = ['modality', 'name', 'order']
    list_filter = ['modality']
    ordering = ['modality', 'order']


class GraduationInline(admin.TabularInline):
    model = StudentGraduation
    extra = 0


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'enrollment_date', 'active']
    list_filter = ['active', 'enrollment_date']
    search_fields = ['name', 'cpf', 'phone', 'email']
    inlines = [GraduationInline]
    ordering = ['name']


@admin.register(StudentGraduation)
class StudentGraduationAdmin(admin.ModelAdmin):
    list_display = ['student', 'modality', 'belt', 'graduation_date']
    list_filter = ['modality', 'belt']
    search_fields = ['student__name']
