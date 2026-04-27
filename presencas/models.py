from django.db import models


class Attendance(models.Model):
    student = models.ForeignKey('alunos.Student', on_delete=models.CASCADE,
                                related_name='attendances', verbose_name='Aluno')
    class_group = models.ForeignKey('turmas.ClassGroup', on_delete=models.CASCADE,
                                    related_name='attendances', verbose_name='Turma')
    date = models.DateField('Data')
    is_present = models.BooleanField('Presente', default=True)
    note = models.CharField('Observação', max_length=200, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    registered_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Registrado por'
    )

    class Meta:
        verbose_name = 'Presença'
        verbose_name_plural = 'Presenças'
        unique_together = ['student', 'class_group', 'date']
        ordering = ['-date', 'student__name']

    def __str__(self):
        status = 'Presente' if self.is_present else 'Faltou'
        return f'{self.student} – {self.class_group} – {self.date} ({status})'
