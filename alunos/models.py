from django.db import models
from django.utils import timezone


class Modality(models.Model):
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição', blank=True)
    active = models.BooleanField('Ativo', default=True)
    seed_key = models.CharField(max_length=50, unique=True, null=True, blank=True, default=None)

    class Meta:
        verbose_name = 'Modalidade'
        verbose_name_plural = 'Modalidades'
        ordering = ['name']

    def __str__(self):
        return self.name


class Belt(models.Model):
    modality = models.ForeignKey(Modality, on_delete=models.CASCADE, related_name='belts')
    name = models.CharField('Nome', max_length=50)
    order = models.PositiveIntegerField('Ordem')
    color_hex = models.CharField('Cor (HEX)', max_length=7, default='#FFFFFF')
    color_hex_2 = models.CharField('Segunda Cor (HEX)', max_length=7, blank=True, default='')

    class Meta:
        verbose_name = 'Faixa'
        verbose_name_plural = 'Faixas'
        ordering = ['modality', 'order']
        unique_together = ['modality', 'order']

    def __str__(self):
        return f'{self.modality} – {self.name}'


class Student(models.Model):
    name = models.CharField('Nome completo', max_length=200)
    cpf = models.CharField('CPF', max_length=14, unique=True, blank=True, null=True)
    birth_date = models.DateField('Data de nascimento')
    phone = models.CharField('Telefone', max_length=20)
    email = models.EmailField('E-mail', blank=True)
    address = models.CharField('Endereço', max_length=300, blank=True)
    photo = models.ImageField('Foto', upload_to='students/', blank=True, null=True)
    enrollment_date = models.DateField('Data de matrícula', default=timezone.now)
    active = models.BooleanField('Ativo', default=True)
    notes = models.TextField('Observações', blank=True)
    guardian_name = models.CharField('Nome do responsável', max_length=200, blank=True)
    guardian_phone = models.CharField('Telefone do responsável', max_length=20, blank=True)
    guardian_cpf = models.CharField('CPF do responsável', max_length=14, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def age(self):
        today = timezone.now().date()
        return (today - self.birth_date).days // 365

    @property
    def is_minor(self):
        return self.age < 18

    @property
    def active_classes_count(self):
        return self.class_enrollments.filter(active=True).count()

    @property
    def current_belt(self):
        grad = self.graduations.order_by('-graduation_date').first()
        return grad.belt if grad else None


class StudentGraduation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='graduations')
    modality = models.ForeignKey(Modality, on_delete=models.CASCADE, verbose_name='Modalidade')
    belt = models.ForeignKey(Belt, on_delete=models.CASCADE, verbose_name='Faixa')
    graduation_date = models.DateField('Data da graduação')
    notes = models.TextField('Observações', blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Graduação'
        verbose_name_plural = 'Graduações'
        ordering = ['-graduation_date']

    def __str__(self):
        return f'{self.student} – {self.belt} ({self.graduation_date})'
