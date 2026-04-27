from django import forms
from .models import Plan, FinancialEnrollment, MonthlyFee, PAYMENT_METHODS
from django.utils import timezone


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['name', 'description', 'amount', 'modalities', 'active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'modalities': forms.CheckboxSelectMultiple(),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FinancialEnrollmentForm(forms.ModelForm):
    class Meta:
        model = FinancialEnrollment
        fields = ['student', 'plan', 'start_date', 'end_date', 'discount_percent', 'active', 'notes']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class MonthlyFeeForm(forms.ModelForm):
    class Meta:
        model = MonthlyFee
        fields = ['student', 'enrollment', 'reference_month', 'amount', 'discount',
                  'status', 'due_date', 'payment_date', 'payment_method', 'notes']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'enrollment': forms.Select(attrs={'class': 'form-select'}),
            'reference_month': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class RegisterPaymentForm(forms.Form):
    payment_date = forms.DateField(
        label='Data do pagamento',
        initial=timezone.now,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    payment_method = forms.ChoiceField(
        label='Forma de pagamento',
        choices=PAYMENT_METHODS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    notes = forms.CharField(
        label='Observações',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )


class GenerateFeesForm(forms.Form):
    reference_month = forms.DateField(
        label='Mês de referência (selecione o 1º dia do mês)',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    due_day = forms.IntegerField(
        label='Dia de vencimento',
        initial=10,
        min_value=1,
        max_value=28,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
