from django import forms
from .models import Student, StudentGraduation, Modality, Belt


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'cpf', 'birth_date', 'phone', 'email', 'address', 'photo',
            'enrollment_date', 'active', 'notes',
            'guardian_name', 'guardian_phone', 'guardian_cpf',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'enrollment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_cpf': forms.TextInput(attrs={'class': 'form-control'}),
        }


class GraduationForm(forms.ModelForm):
    class Meta:
        model = StudentGraduation
        fields = ['modality', 'belt', 'graduation_date', 'notes']
        widgets = {
            'modality': forms.Select(attrs={'class': 'form-select', 'id': 'id_modality'}),
            'belt': forms.Select(attrs={'class': 'form-select', 'id': 'id_belt'}),
            'graduation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ModalityForm(forms.ModelForm):
    class Meta:
        model = Modality
        fields = ['name', 'description', 'active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BeltForm(forms.ModelForm):
    class Meta:
        model = Belt
        fields = ['modality', 'name', 'order', 'color_hex', 'color_hex_2']
        widgets = {
            'modality': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'color_hex': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'color_hex_2': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }
