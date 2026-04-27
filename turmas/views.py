from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ClassGroup, ClassSchedule, Instructor, ClassEnrollment
from .forms import ClassGroupForm, ClassScheduleForm, InstructorForm
from alunos.models import Student


@login_required
def class_list(request):
    classes = ClassGroup.objects.filter(active=True).select_related(
        'modality', 'instructor'
    ).prefetch_related('schedules', 'enrollments')
    return render(request, 'turmas/lista.html', {'classes': classes})


@login_required
def class_detail(request, pk):
    training_class = get_object_or_404(ClassGroup, pk=pk)
    enrollments = training_class.enrollments.filter(active=True).select_related('student')
    schedules = training_class.schedules.all()
    return render(request, 'turmas/detalhe.html', {
        'training_class': training_class,
        'enrollments': enrollments,
        'schedules': schedules,
    })


@login_required
def class_create(request):
    if request.method == 'POST':
        form = ClassGroupForm(request.POST)
        if form.is_valid():
            training_class = form.save()
            messages.success(request, f'Turma "{training_class.name}" criada!')
            return redirect('classes:detail', pk=training_class.pk)
    else:
        form = ClassGroupForm()
    return render(request, 'turmas/form.html', {'form': form, 'title': 'Nova Turma'})


@login_required
def class_update(request, pk):
    training_class = get_object_or_404(ClassGroup, pk=pk)
    if request.method == 'POST':
        form = ClassGroupForm(request.POST, instance=training_class)
        if form.is_valid():
            form.save()
            messages.success(request, f'Turma "{training_class.name}" atualizada!')
            return redirect('classes:detail', pk=training_class.pk)
    else:
        form = ClassGroupForm(instance=training_class)
    return render(request, 'turmas/form.html', {
        'form': form, 'title': f'Editar – {training_class.name}', 'training_class': training_class
    })


@login_required
def schedule_add(request, class_pk):
    training_class = get_object_or_404(ClassGroup, pk=class_pk)
    if request.method == 'POST':
        form = ClassScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.class_group = training_class
            schedule.save()
            messages.success(request, 'Horário adicionado!')
            return redirect('classes:detail', pk=training_class.pk)
    else:
        form = ClassScheduleForm()
    return render(request, 'turmas/horario_form.html', {'form': form, 'training_class': training_class})


@login_required
def schedule_remove(request, pk):
    schedule = get_object_or_404(ClassSchedule, pk=pk)
    class_pk = schedule.class_group.pk
    schedule.delete()
    messages.success(request, 'Horário removido.')
    return redirect('classes:detail', pk=class_pk)


@login_required
def enrollment_add(request, class_pk):
    training_class = get_object_or_404(ClassGroup, pk=class_pk)
    enrolled_ids = training_class.enrollments.filter(active=True).values_list('student_id', flat=True)
    available_students = Student.objects.filter(active=True).exclude(id__in=enrolled_ids)

    if request.method == 'POST':
        student = get_object_or_404(Student, pk=request.POST.get('student'))
        enrollment, created = ClassEnrollment.objects.get_or_create(
            student=student, class_group=training_class
        )
        if not created:
            enrollment.active = True
            enrollment.save()
        messages.success(request, f'{student.name} matriculado em {training_class.name}!')
        return redirect('classes:detail', pk=training_class.pk)

    return render(request, 'turmas/matricula_form.html', {
        'training_class': training_class,
        'available_students': available_students,
    })


@login_required
def enrollment_remove(request, pk):
    enrollment = get_object_or_404(ClassEnrollment, pk=pk)
    class_pk = enrollment.class_group.pk
    enrollment.active = False
    enrollment.save()
    messages.success(request, f'{enrollment.student.name} removido da turma.')
    return redirect('classes:detail', pk=class_pk)


@login_required
def instructor_list(request):
    instructors = Instructor.objects.filter(active=True).prefetch_related('modalities')
    return render(request, 'turmas/instrutores.html', {'instructors': instructors})


@login_required
def instructor_create(request):
    if request.method == 'POST':
        form = InstructorForm(request.POST)
        if form.is_valid():
            instructor = form.save()
            messages.success(request, f'Instrutor {instructor.name} cadastrado!')
            return redirect('classes:instructors')
    else:
        form = InstructorForm()
    return render(request, 'turmas/instrutor_form.html', {'form': form, 'title': 'Novo Instrutor'})


@login_required
def instructor_update(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)
    if request.method == 'POST':
        form = InstructorForm(request.POST, instance=instructor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Instrutor {instructor.name} atualizado!')
            return redirect('classes:instructors')
    else:
        form = InstructorForm(instance=instructor)
    return render(request, 'turmas/instrutor_form.html', {
        'form': form, 'title': f'Editar – {instructor.name}', 'instructor': instructor,
    })
