from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta

from alunos.models import Student
from turmas.models import ClassGroup, ClassSchedule
from presencas.models import Attendance
from financeiro.models import MonthlyFee
from core.management.commands.populate import Command as PopulateCommand


def demo_logout(request):
    logout(request)
    Student.objects.all().delete()
    PopulateCommand().handle()
    return redirect('login')


@login_required
def dashboard(request):
    today = date.today()

    total_students = Student.objects.filter(active=True).count()
    total_classes = ClassGroup.objects.filter(active=True).count()

    today_schedules = ClassSchedule.objects.filter(
        weekday=today.weekday(),
        class_group__active=True,
    ).select_related('class_group', 'class_group__modality', 'class_group__instructor').order_by('start_time')

    today_attendances = Attendance.objects.filter(date=today, is_present=True).count()

    overdue_fees = MonthlyFee.objects.filter(
        status__in=['pending', 'overdue'],
        due_date__lt=today,
    ).select_related('student').order_by('due_date')[:10]

    total_overdue = MonthlyFee.objects.filter(
        status__in=['pending', 'overdue'],
        due_date__lt=today,
    ).count()

    upcoming_fees = MonthlyFee.objects.filter(
        status='pending',
        due_date__range=[today, today + timedelta(days=7)],
    ).select_related('student').order_by('due_date')[:5]

    birthdays = Student.objects.filter(
        active=True,
        birth_date__month=today.month,
    ).order_by('birth_date__day')[:5]

    recent_attendances = Attendance.objects.filter(
        date=today,
    ).select_related('student', 'class_group').order_by('-registered_at')[:8]

    return render(request, 'core/dashboard.html', {
        'today': today,
        'total_students': total_students,
        'total_classes': total_classes,
        'today_attendances': today_attendances,
        'total_overdue': total_overdue,
        'today_schedules': today_schedules,
        'overdue_fees': overdue_fees,
        'upcoming_fees': upcoming_fees,
        'birthdays': birthdays,
        'recent_attendances': recent_attendances,
    })
