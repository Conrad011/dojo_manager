import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand


FIRST_NAMES = [
    'Gabriel', 'Lucas', 'Mateus', 'Pedro', 'Rafael', 'Felipe', 'Thiago', 'Bruno', 'Diego', 'Rodrigo',
    'João', 'André', 'Carlos', 'Daniel', 'Eduardo', 'Fernando', 'Gustavo', 'Henrique', 'Igor', 'Julio',
    'Ana', 'Beatriz', 'Camila', 'Daniela', 'Fernanda', 'Gabriela', 'Helena', 'Isabella', 'Julia', 'Karen',
    'Larissa', 'Mariana', 'Natalia', 'Patricia', 'Renata', 'Sandra', 'Tatiana', 'Vanessa', 'Amanda', 'Bruna',
    'Leonardo', 'Marcelo', 'Nicolas', 'Otavio', 'Paulo', 'Ricardo', 'Sergio', 'Vitor', 'William', 'Alexandre',
]

LAST_NAMES = [
    'Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves', 'Pereira', 'Lima', 'Gomes',
    'Costa', 'Ribeiro', 'Martins', 'Carvalho', 'Almeida', 'Lopes', 'Sousa', 'Fernandes', 'Vieira', 'Barbosa',
    'Rocha', 'Dias', 'Nascimento', 'Andrade', 'Moreira', 'Nunes', 'Marques', 'Machado', 'Mendes', 'Freitas',
]

CITIES = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre', 'Salvador', 'Fortaleza']


def random_cpf(used):
    while True:
        digits = [random.randint(0, 9) for _ in range(11)]
        cpf = f'{"".join(str(d) for d in digits[:3])}.{"".join(str(d) for d in digits[3:6])}.{"".join(str(d) for d in digits[6:9])}-{"".join(str(d) for d in digits[9:])}'
        if cpf not in used:
            used.add(cpf)
            return cpf


def random_phone():
    return f'({random.randint(11, 99)}) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}'


def random_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


class Command(BaseCommand):
    help = 'Populate database with 100 sample students and related data'

    def handle(self, *args, **options):
        from alunos.models import Modality, Belt, Student, StudentGraduation
        from turmas.models import ClassGroup, ClassEnrollment
        from financeiro.models import Plan, FinancialEnrollment, MonthlyFee
        from presencas.models import Attendance

        modalities = list(Modality.objects.all())
        classes = list(ClassGroup.objects.filter(active=True))
        plans = list(Plan.objects.filter(active=True))

        if not modalities or not classes or not plans:
            self.stdout.write(self.style.ERROR('Run "python manage.py seed" first.'))
            return

        today = date.today()
        used_cpfs = set()
        created = 0

        self.stdout.write('Creating 100 students...')
        students = []
        for _ in range(100):
            name = f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}'
            birth = random_date(date(1985, 1, 1), date(2012, 12, 31))
            enrollment = random_date(date(2023, 1, 1), today)
            city = random.choice(CITIES)
            age = (today - birth).days // 365

            student, new = Student.objects.get_or_create(
                cpf=random_cpf(used_cpfs),
                defaults={
                    'name': name,
                    'birth_date': birth,
                    'phone': random_phone(),
                    'email': f'{name.lower().replace(" ", ".")}@email.com',
                    'address': f'Rua das Artes, {random.randint(1, 999)} – {city}',
                    'enrollment_date': enrollment,
                    'active': random.random() > 0.1,
                    'guardian_name': f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}' if age < 18 else '',
                    'guardian_phone': random_phone() if age < 18 else '',
                },
            )
            if new:
                created += 1
            students.append(student)

        self.stdout.write(f'  {created} students created.')

        self.stdout.write('Enrolling students in classes...')
        enrollments_created = 0
        for student in students:
            num_classes = random.randint(1, 2)
            chosen_classes = random.sample(classes, min(num_classes, len(classes)))
            for cg in chosen_classes:
                _, new = ClassEnrollment.objects.get_or_create(student=student, class_group=cg)
                if new:
                    enrollments_created += 1

        self.stdout.write(f'  {enrollments_created} class enrollments created.')

        self.stdout.write('Creating financial enrollments and monthly fees...')
        fees_created = 0
        for student in students:
            plan = random.choice(plans)
            fin_enroll, _ = FinancialEnrollment.objects.get_or_create(
                student=student,
                defaults={
                    'plan': plan,
                    'start_date': student.enrollment_date,
                    'active': student.active,
                    'discount_percent': Decimal(random.choice([0, 0, 0, 5, 10])),
                },
            )

            months_back = 6
            for i in range(months_back, -1, -1):
                ref_month = date(today.year, today.month, 1) - timedelta(days=i * 30)
                ref_month = ref_month.replace(day=1)
                due = ref_month.replace(day=10)

                discount = fin_enroll.plan.amount * (fin_enroll.discount_percent / 100)
                net = fin_enroll.plan.amount - discount

                if ref_month < date(today.year, today.month, 1):
                    status = random.choices(['paid', 'overdue'], weights=[85, 15])[0]
                    payment_date = due + timedelta(days=random.randint(-5, 15)) if status == 'paid' else None
                    payment_method = random.choice(['pix', 'cash', 'debit_card']) if status == 'paid' else ''
                else:
                    status = 'pending'
                    payment_date = None
                    payment_method = ''

                _, new = MonthlyFee.objects.get_or_create(
                    student=student,
                    reference_month=ref_month,
                    defaults={
                        'enrollment': fin_enroll,
                        'amount': net,
                        'discount': discount,
                        'status': status,
                        'due_date': due,
                        'payment_date': payment_date,
                        'payment_method': payment_method,
                    },
                )
                if new:
                    fees_created += 1

        self.stdout.write(f'  {fees_created} monthly fees created.')

        self.stdout.write('Creating attendance records (last 30 days)...')
        attendance_created = 0
        for i in range(30):
            day = today - timedelta(days=i)
            if day.weekday() >= 6:
                continue
            daily_students = random.sample(students, min(random.randint(10, 30), len(students)))
            for student in daily_students:
                enrollments = list(student.class_enrollments.filter(active=True))
                if not enrollments:
                    continue
                enroll = random.choice(enrollments)
                _, new = Attendance.objects.get_or_create(
                    student=student,
                    class_group=enroll.class_group,
                    date=day,
                    defaults={'is_present': random.random() > 0.05},
                )
                if new:
                    attendance_created += 1

        self.stdout.write(f'  {attendance_created} attendance records created.')

        self.stdout.write('Adding graduations to some students...')
        grad_created = 0
        for student in random.sample(students, int(len(students) * 0.6)):
            enroll = student.class_enrollments.filter(active=True).first()
            if not enroll:
                continue
            modality = enroll.class_group.modality
            belts = list(modality.belts.order_by('order'))
            if not belts:
                continue
            num_belts = random.randint(1, min(3, len(belts)))
            grad_date = student.enrollment_date
            for belt in belts[:num_belts]:
                grad_date = grad_date + timedelta(days=random.randint(90, 365))
                if grad_date > today:
                    break
                StudentGraduation.objects.get_or_create(
                    student=student,
                    modality=modality,
                    belt=belt,
                    defaults={'graduation_date': grad_date},
                )
                grad_created += 1

        self.stdout.write(f'  {grad_created} graduations created.')
        self.stdout.write(self.style.SUCCESS('\nDatabase populated successfully!'))
