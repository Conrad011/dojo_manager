from django.db import models
from django.contrib.auth.models import User


WEEKDAYS = [
    (0, 'Segunda-feira'),
    (1, 'Terça-feira'),
    (2, 'Quarta-feira'),
    (3, 'Quinta-feira'),
    (4, 'Sexta-feira'),
    (5, 'Sábado'),
    (6, 'Domingo'),
]

WEEKDAYS_ABBR = {
    0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui',
    4: 'Sex', 5: 'Sáb', 6: 'Dom',
}


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='Usuário')
    name = models.CharField('Nome completo', max_length=200)
    cpf = models.CharField('CPF', max_length=14, blank=True)
    phone = models.CharField('Telefone', max_length=20)
    email = models.EmailField('E-mail', blank=True)
    modalities = models.ManyToManyField('alunos.Modality', blank=True, verbose_name='Modalidades')
    active = models.BooleanField('Ativo', default=True)
    bio = models.TextField('Bio / Formação', blank=True)

    class Meta:
        verbose_name = 'Instrutor'
        verbose_name_plural = 'Instrutores'
        ordering = ['name']

    def __str__(self):
        return self.name


class ClassGroup(models.Model):
    name = models.CharField('Nome da turma', max_length=200)
    modality = models.ForeignKey('alunos.Modality', on_delete=models.CASCADE,
                                 verbose_name='Modalidade')
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='Instrutor')
    max_capacity = models.PositiveIntegerField('Capacidade máxima', default=30)
    active = models.BooleanField('Ativa', default=True)
    description = models.TextField('Descrição', blank=True)

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        ordering = ['modality', 'name']

    def __str__(self):
        return f'{self.name} ({self.modality})'

    @property
    def total_students(self):
        return self.enrollments.filter(active=True).count()

    def schedules_display(self):
        return ', '.join(
            f'{WEEKDAYS_ABBR[s.weekday]} {s.start_time.strftime("%H:%M")}'
            for s in self.schedules.all()
        )


class ClassSchedule(models.Model):
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name='schedules')
    weekday = models.IntegerField('Dia da semana', choices=WEEKDAYS)
    start_time = models.TimeField('Início')
    end_time = models.TimeField('Fim')

    class Meta:
        verbose_name = 'Horário'
        verbose_name_plural = 'Horários'
        ordering = ['weekday', 'start_time']

    def __str__(self):
        return f'{self.class_group} – {self.get_weekday_display()} {self.start_time.strftime("%H:%M")}'


class ClassEnrollment(models.Model):
    student = models.ForeignKey('alunos.Student', on_delete=models.CASCADE,
                                related_name='class_enrollments', verbose_name='Aluno')
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE,
                                    related_name='enrollments', verbose_name='Turma')
    enrollment_date = models.DateField('Data de matrícula', auto_now_add=True)
    active = models.BooleanField('Ativa', default=True)

    class Meta:
        verbose_name = 'Matrícula em Turma'
        verbose_name_plural = 'Matrículas em Turmas'
        unique_together = ['student', 'class_group']
        ordering = ['-enrollment_date']

    def __str__(self):
        return f'{self.student} → {self.class_group}'
