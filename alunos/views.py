from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Student, StudentGraduation, Modality, Belt
from .forms import StudentForm, GraduationForm, ModalityForm, BeltForm


@login_required
def student_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', 'active')
    students = Student.objects.all()

    if q:
        students = students.filter(Q(name__icontains=q) | Q(cpf__icontains=q) | Q(phone__icontains=q))

    if status == 'active':
        students = students.filter(active=True)
    elif status == 'inactive':
        students = students.filter(active=False)

    return render(request, 'alunos/lista.html', {
        'students': students,
        'q': q,
        'status': status,
        'total': students.count(),
    })


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    graduations = student.graduations.select_related('modality', 'belt').order_by('-graduation_date')
    class_enrollments = student.class_enrollments.filter(active=True).select_related(
        'class_group', 'class_group__modality'
    )
    fees = student.monthly_fees.order_by('-due_date')[:12]
    recent_attendances = student.attendances.filter(is_present=True).select_related(
        'class_group'
    ).order_by('-date')[:10]

    return render(request, 'alunos/detalhe.html', {
        'student': student,
        'graduations': graduations,
        'class_enrollments': class_enrollments,
        'fees': fees,
        'recent_attendances': recent_attendances,
    })


@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Aluno {student.name} cadastrado com sucesso!')
            return redirect('students:detail', pk=student.pk)
    else:
        form = StudentForm()
    return render(request, 'alunos/form.html', {'form': form, 'title': 'Novo Aluno'})


@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Aluno {student.name} atualizado com sucesso!')
            return redirect('students:detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    return render(request, 'alunos/form.html', {
        'form': form, 'title': f'Editar – {student.name}', 'student': student
    })


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.active = False
        student.save()
        messages.success(request, f'Aluno {student.name} desativado.')
        return redirect('students:list')
    return render(request, 'alunos/confirmar_exclusao.html', {'student': student})


@login_required
def graduation_add(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = GraduationForm(request.POST)
        if form.is_valid():
            grad = form.save(commit=False)
            grad.student = student
            grad.save()
            messages.success(request, f'Graduação registrada: {grad.belt}')
            return redirect('students:detail', pk=student.pk)
    else:
        form = GraduationForm()
    return render(request, 'alunos/graduacao_form.html', {'form': form, 'student': student})


@login_required
def belts_by_modality(request):
    modality_id = request.GET.get('modality_id')
    belts = Belt.objects.filter(modality_id=modality_id).order_by('order')
    return JsonResponse({'belts': [
        {'id': b.id, 'name': b.name, 'color_hex': b.color_hex, 'color_hex_2': b.color_hex_2}
        for b in belts
    ]})


@login_required
def modality_list(request):
    modalities = Modality.objects.prefetch_related('belts').all()
    return render(request, 'alunos/modalidades.html', {'modalities': modalities})


@login_required
def modality_create(request):
    if request.method == 'POST':
        form = ModalityForm(request.POST)
        if form.is_valid():
            modality = form.save()
            messages.success(request, f'Modalidade {modality.name} criada!')
            return redirect('students:modalities')
    else:
        form = ModalityForm()
    return render(request, 'alunos/modalidade_form.html', {'form': form, 'title': 'Nova Modalidade'})


@login_required
def belt_create(request, modality_pk):
    modality = get_object_or_404(Modality, pk=modality_pk)
    if request.method == 'POST':
        form = BeltForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faixa adicionada!')
            return redirect('students:modalities')
    else:
        form = BeltForm(initial={'modality': modality})
    return render(request, 'alunos/modalidade_form.html', {
        'form': form, 'title': f'Nova Faixa – {modality.name}', 'modality': modality,
    })
