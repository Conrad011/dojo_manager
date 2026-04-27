from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, datetime
from .models import Attendance
from turmas.models import ClassGroup, ClassEnrollment
from alunos.models import Student


@login_required
def register_attendance(request, class_pk, date_str=None):
    training_class = get_object_or_404(ClassGroup, pk=class_pk)
    class_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

    enrollments = ClassEnrollment.objects.filter(
        class_group=training_class, active=True
    ).select_related('student').order_by('student__name')

    existing_attendance = {
        a.student_id: a for a in Attendance.objects.filter(class_group=training_class, date=class_date)
    }

    if request.method == 'POST':
        present_ids = set(map(int, request.POST.getlist('present_ids')))
        for enrollment in enrollments:
            student = enrollment.student
            Attendance.objects.update_or_create(
                student=student,
                class_group=training_class,
                date=class_date,
                defaults={'is_present': student.id in present_ids, 'registered_by': request.user}
            )
        messages.success(request, f'Chamada da turma {training_class.name} ({class_date}) salva!')
        return redirect('core:dashboard')

    attendance_list = []
    for enrollment in enrollments:
        student = enrollment.student
        record = existing_attendance.get(student.id)
        attendance_list.append({
            'student': student,
            'is_present': record.is_present if record else True,
            'note': record.note if record else '',
        })

    return render(request, 'presencas/registrar.html', {
        'training_class': training_class,
        'class_date': class_date,
        'attendance_list': attendance_list,
        'already_registered': bool(existing_attendance),
    })


@login_required
def quick_checkin(request):
    classes = ClassGroup.objects.filter(active=True).select_related('modality').order_by('name')

    if request.method == 'POST':
        student = get_object_or_404(Student, pk=request.POST.get('student_id'))
        training_class = get_object_or_404(ClassGroup, pk=request.POST.get('class_id'))
        record, created = Attendance.objects.get_or_create(
            student=student,
            class_group=training_class,
            date=date.today(),
            defaults={'is_present': True, 'registered_by': request.user}
        )
        if not created:
            record.is_present = True
            record.registered_by = request.user
            record.save()
        messages.success(request, f'Check-in de {student.name} registrado em {training_class.name}!')
        return redirect('attendance:checkin')

    q = request.GET.get('q', '')
    student_results = Student.objects.filter(name__icontains=q, active=True)[:10] if q else []

    return render(request, 'presencas/checkin.html', {
        'classes': classes,
        'student_results': student_results,
        'q': q,
    })


@login_required
def attendance_report(request):
    all_classes = ClassGroup.objects.filter(active=True)

    class_id = request.GET.get('class_group')
    start_date = request.GET.get('start_date', date.today().replace(day=1).isoformat())
    end_date = request.GET.get('end_date', date.today().isoformat())

    records = Attendance.objects.select_related('student', 'class_group').filter(
        date__range=[start_date, end_date]
    )
    if class_id:
        records = records.filter(class_group_id=class_id)

    data = {}
    for record in records:
        key = (record.class_group.name, record.student.name)
        if key not in data:
            data[key] = {'present': 0, 'absent': 0}
        if record.is_present:
            data[key]['present'] += 1
        else:
            data[key]['absent'] += 1

    summary = [
        {
            'class_name': k[0],
            'student_name': k[1],
            'present_count': v['present'],
            'absent_count': v['absent'],
            'total': v['present'] + v['absent'],
        }
        for k, v in sorted(data.items())
    ]

    return render(request, 'presencas/relatorio.html', {
        'all_classes': all_classes,
        'selected_class': class_id,
        'start_date': start_date,
        'end_date': end_date,
        'summary': summary,
        'total_present': sum(r['present_count'] for r in summary),
        'total_absent': sum(r['absent_count'] for r in summary),
    })


@login_required
def student_history(request, student_pk):
    student = get_object_or_404(Student, pk=student_pk)
    attendances = Attendance.objects.filter(student=student).select_related('class_group').order_by('-date')

    total = attendances.count()
    total_present = attendances.filter(is_present=True).count()
    percentage = round((total_present / total * 100) if total > 0 else 0, 1)

    return render(request, 'presencas/historico_aluno.html', {
        'student': student,
        'attendances': attendances,
        'total': total,
        'total_present': total_present,
        'total_absent': total - total_present,
        'percentage': percentage,
    })
