from django.db import models
from django.utils import timezone
from decimal import Decimal


FEE_STATUS = [
    ('pending', 'Pendente'),
    ('paid', 'Pago'),
    ('overdue', 'Atrasado'),
    ('cancelled', 'Cancelado'),
]

PAYMENT_METHODS = [
    ('cash', 'Dinheiro'),
    ('pix', 'PIX'),
    ('debit_card', 'Cartão de Débito'),
    ('credit_card', 'Cartão de Crédito'),
    ('bank_slip', 'Boleto'),
    ('transfer', 'Transferência Bancária'),
]


class Plan(models.Model):
    name = models.CharField('Nome do plano', max_length=100)
    description = models.TextField('Descrição', blank=True)
    amount = models.DecimalField('Valor (R$)', max_digits=10, decimal_places=2)
    modalities = models.ManyToManyField('alunos.Modality', blank=True,
                                        verbose_name='Modalidades incluídas')
    active = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'
        ordering = ['amount']

    def __str__(self):
        return f'{self.name} – R$ {self.amount}'


class FinancialEnrollment(models.Model):
    student = models.ForeignKey('alunos.Student', on_delete=models.CASCADE,
                                related_name='financial_enrollments', verbose_name='Aluno')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, verbose_name='Plano')
    start_date = models.DateField('Início')
    end_date = models.DateField('Fim', null=True, blank=True)
    discount_percent = models.DecimalField('Desconto (%)', max_digits=5, decimal_places=2,
                                           default=Decimal('0.00'))
    active = models.BooleanField('Ativa', default=True)
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Matrícula Financeira'
        verbose_name_plural = 'Matrículas Financeiras'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.student} – {self.plan}'

    @property
    def discounted_amount(self):
        if self.plan:
            discount = self.plan.amount * (self.discount_percent / 100)
            return self.plan.amount - discount
        return Decimal('0.00')


class MonthlyFee(models.Model):
    student = models.ForeignKey('alunos.Student', on_delete=models.CASCADE,
                                related_name='monthly_fees', verbose_name='Aluno')
    enrollment = models.ForeignKey(FinancialEnrollment, on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name='Matrícula')
    reference_month = models.DateField('Mês de referência')
    amount = models.DecimalField('Valor (R$)', max_digits=10, decimal_places=2)
    discount = models.DecimalField('Desconto (R$)', max_digits=10, decimal_places=2,
                                   default=Decimal('0.00'))
    status = models.CharField('Status', max_length=20, choices=FEE_STATUS, default='pending')
    due_date = models.DateField('Vencimento')
    payment_date = models.DateField('Data de pagamento', null=True, blank=True)
    payment_method = models.CharField('Forma de pagamento', max_length=20,
                                      choices=PAYMENT_METHODS, blank=True)
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mensalidade'
        verbose_name_plural = 'Mensalidades'
        ordering = ['-due_date']
        unique_together = ['student', 'reference_month']

    def __str__(self):
        return f'{self.student} – {self.reference_month.strftime("%m/%Y")} ({self.get_status_display()})'

    @property
    def net_amount(self):
        return self.amount - self.discount

    def save(self, *args, **kwargs):
        today = timezone.now().date()
        if self.status == 'pending' and self.due_date < today:
            self.status = 'overdue'
        super().save(*args, **kwargs)
