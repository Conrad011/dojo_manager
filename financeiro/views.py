from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, F, ExpressionWrapper, DecimalField
from datetime import date
from decimal import Decimal

from .models import Plan, FinancialEnrollment, MonthlyFee
from .forms import PlanForm, FinancialEnrollmentForm, MonthlyFeeForm, RegisterPaymentForm, GenerateFeesForm


_NET_AMOUNT = ExpressionWrapper(F('amount') - F('discount'), output_field=DecimalField())


@login_required
def financial_dashboard(request):
    today = date.today()

    def _total(status):
        return MonthlyFee.objects.filter(status=status).aggregate(
            total=Sum(_NET_AMOUNT)
        )['total'] or Decimal('0.00')

    total_pending = _total('pending')
    total_overdue_amount = _total('overdue')
    total_received_month = MonthlyFee.objects.filter(
        status='paid',
        payment_date__month=today.month,
        payment_date__year=today.year,
    ).aggregate(total=Sum(_NET_AMOUNT))['total'] or Decimal('0.00')

    overdue_fees = MonthlyFee.objects.filter(status='overdue').select_related('student').order_by('due_date')[:15]
    today_fees = MonthlyFee.objects.filter(due_date=today, status='pending').select_related('student')
    recent_payments = MonthlyFee.objects.filter(
        status='paid', payment_date=today,
    ).select_related('student').order_by('-updated_at')[:10]

    return render(request, 'financeiro/dashboard.html', {
        'total_pending': total_pending,
        'total_overdue_amount': total_overdue_amount,
        'total_received_month': total_received_month,
        'overdue_fees': overdue_fees,
        'today_fees': today_fees,
        'recent_payments': recent_payments,
        'today': today,
    })


@login_required
def fee_list(request):
    today = date.today()
    MonthlyFee.objects.filter(status='pending', due_date__lt=today).update(status='overdue')

    status_filter = request.GET.get('status', '')
    month_filter = request.GET.get('month', '')
    student_q = request.GET.get('student', '')

    fees = MonthlyFee.objects.select_related('student').order_by('-due_date')

    if status_filter:
        fees = fees.filter(status=status_filter)
    if student_q:
        fees = fees.filter(student__name__icontains=student_q)
    if month_filter:
        try:
            year, month = month_filter.split('-')
            fees = fees.filter(reference_month__year=int(year), reference_month__month=int(month))
        except (ValueError, AttributeError):
            pass

    return render(request, 'financeiro/mensalidades.html', {
        'fees': fees[:100],
        'status_filter': status_filter,
        'month_filter': month_filter,
        'student_q': student_q,
        'total': fees.count(),
    })


@login_required
def fee_create(request):
    if request.method == 'POST':
        form = MonthlyFeeForm(request.POST)
        if form.is_valid():
            fee = form.save()
            messages.success(request, f'Mensalidade de {fee.student.name} criada!')
            return redirect('financial:fees')
    else:
        form = MonthlyFeeForm()
    return render(request, 'financeiro/mensalidade_form.html', {'form': form, 'title': 'Nova Mensalidade'})


@login_required
def fee_update(request, pk):
    fee = get_object_or_404(MonthlyFee, pk=pk)
    if request.method == 'POST':
        form = MonthlyFeeForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensalidade atualizada!')
            return redirect('financial:fees')
    else:
        form = MonthlyFeeForm(instance=fee)
    return render(request, 'financeiro/mensalidade_form.html', {
        'form': form, 'title': f'Editar Mensalidade – {fee.student.name}', 'fee': fee,
    })


@login_required
def register_payment(request, pk):
    fee = get_object_or_404(MonthlyFee, pk=pk)
    if request.method == 'POST':
        form = RegisterPaymentForm(request.POST)
        if form.is_valid():
            fee.status = 'paid'
            fee.payment_date = form.cleaned_data['payment_date']
            fee.payment_method = form.cleaned_data['payment_method']
            if form.cleaned_data['notes']:
                fee.notes = form.cleaned_data['notes']
            fee.save()
            messages.success(request, f'Pagamento de {fee.student.name} registrado!')
            return redirect('financial:fees')
    else:
        form = RegisterPaymentForm()
    return render(request, 'financeiro/registrar_pagamento.html', {'form': form, 'fee': fee})


@login_required
def plan_list(request):
    plans = Plan.objects.prefetch_related('modalities').filter(active=True)
    return render(request, 'financeiro/planos.html', {'plans': plans})


@login_required
def plan_create(request):
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Plano "{plan.name}" criado!')
            return redirect('financial:plans')
    else:
        form = PlanForm()
    return render(request, 'financeiro/plano_form.html', {'form': form, 'title': 'Novo Plano'})


@login_required
def plan_update(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f'Plano "{plan.name}" atualizado!')
            return redirect('financial:plans')
    else:
        form = PlanForm(instance=plan)
    return render(request, 'financeiro/plano_form.html', {
        'form': form, 'title': f'Editar Plano – {plan.name}', 'plan': plan,
    })


@login_required
def financial_enrollment_create(request):
    if request.method == 'POST':
        form = FinancialEnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(request, f'Matrícula financeira de {enrollment.student.name} criada!')
            return redirect('students:detail', pk=enrollment.student.pk)
    else:
        student_id = request.GET.get('student')
        form = FinancialEnrollmentForm(initial={'student': student_id} if student_id else {})
    return render(request, 'financeiro/matricula_form.html', {'form': form, 'title': 'Nova Matrícula Financeira'})


@login_required
def generate_fees(request):
    if request.method == 'POST':
        form = GenerateFeesForm(request.POST)
        if form.is_valid():
            reference_month = form.cleaned_data['reference_month']
            due_day = form.cleaned_data['due_day']
            due_date = reference_month.replace(day=due_day)

            enrollments = FinancialEnrollment.objects.filter(
                Q(end_date__isnull=True) | Q(end_date__gte=reference_month),
                active=True,
                start_date__lte=reference_month,
            )

            created_count = 0
            skipped_count = 0
            for enrollment in enrollments:
                _, created = MonthlyFee.objects.get_or_create(
                    student=enrollment.student,
                    reference_month=reference_month,
                    defaults={
                        'enrollment': enrollment,
                        'amount': enrollment.discounted_amount,
                        'discount': Decimal('0.00'),
                        'status': 'pending',
                        'due_date': due_date,
                    },
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

            messages.success(
                request,
                f'{created_count} mensalidades geradas para {reference_month.strftime("%m/%Y")}. '
                f'{skipped_count} ignoradas (já existiam).',
            )
            return redirect('financial:fees')
    else:
        form = GenerateFeesForm()
    return render(request, 'financeiro/gerar_mensalidades.html', {'form': form, 'title': 'Gerar Mensalidades'})


@login_required
def receipt(request, pk):
    fee = get_object_or_404(MonthlyFee, pk=pk, status='paid')
    return render(request, 'financeiro/recibo.html', {'fee': fee})
