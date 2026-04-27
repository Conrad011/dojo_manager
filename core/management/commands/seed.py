from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Seed initial system data'

    def handle(self, *args, **options):
        from alunos.models import Modality, Belt
        from financeiro.models import Plan

        self.stdout.write('Creating modalities and belts...')

        # BJJ
        bjj, _ = Modality.objects.update_or_create(
            seed_key='bjj',
            defaults={'name': 'Brazilian Jiu-Jitsu (BJJ)'},
        )
        for name, order, color_hex in [
            ('White', 1, '#FFFFFF'),
            ('Blue', 2, '#0066CC'),
            ('Purple', 3, '#660099'),
            ('Brown', 4, '#8B4513'),
            ('Black', 5, '#1a1a1a'),
        ]:
            Belt.objects.update_or_create(
                modality=bjj,
                name=name,
                defaults={
                    'order': order,
                    'color_hex': color_hex
                }
            )

        # JUDO
        judo, _ = Modality.objects.update_or_create(
            seed_key='judo',
            defaults={'name': 'Judo'},
        )
        for name, order, color_hex in [
            ('White', 1, '#FFFFFF'),
            ('Yellow', 2, '#FFD700'),
            ('Orange', 3, '#FF8C00'),
            ('Green', 4, '#228B22'),
            ('Blue', 5, '#0066CC'),
            ('Brown', 6, '#8B4513'),
            ('Black', 7, '#1a1a1a'),
        ]:
            Belt.objects.update_or_create(
                modality=judo,
                name=name,
                defaults={
                    'order': order,
                    'color_hex': color_hex
                }
            )

        # KARATE
        karate, _ = Modality.objects.update_or_create(
            seed_key='karate',
            defaults={'name': 'Karate'},
        )
        for name, order, color_hex in [
            ('White', 1, '#FFFFFF'),
            ('Yellow', 2, '#FFD700'),
            ('Orange', 3, '#FF8C00'),
            ('Green', 4, '#228B22'),
            ('Purple', 5, '#660099'),
            ('Brown', 6, '#8B4513'),
            ('Black', 7, '#1a1a1a'),
        ]:
            Belt.objects.update_or_create(
                modality=karate,
                name=name,
                defaults={
                    'order': order,
                    'color_hex': color_hex
                }
            )

        # MUAY THAI
        muay_thai, _ = Modality.objects.update_or_create(
            seed_key='muay_thai',
            defaults={'name': 'Muay Thai'},
        )
        for name, order, color_hex, color_hex_2 in [
            ('White',           1, '#FFFFFF', ''),
            ('Orange',          2, '#FF8C00', ''),
            ('Orange and Blue', 3, '#FF8C00', '#0066CC'),
            ('Blue',            4, '#0066CC', ''),
            ('Green',           5, '#228B22', ''),
            ('Brown',           6, '#8B4513', ''),
            ('Brown and Black', 7, '#8B4513', '#1a1a1a'),
            ('Black',           8, '#1a1a1a', ''),
        ]:
            Belt.objects.update_or_create(
                modality=muay_thai,
                name=name,
                defaults={
                    'order': order,
                    'color_hex': color_hex,
                    'color_hex_2': color_hex_2
                }
            )

        # CLASSES
        self.stdout.write('Creating classes...')
        from turmas.models import ClassGroup
        for name, modality, capacity in [
            ('BJJ – Beginners',     bjj,       20),
            ('BJJ – Advanced',      bjj,       15),
            ('Judo – All levels',   judo,      20),
            ('Karate – Beginners',  karate,    20),
            ('Muay Thai',           muay_thai, 20),
        ]:
            ClassGroup.objects.update_or_create(
                name=name,
                defaults={'modality': modality, 'max_capacity': capacity, 'active': True},
            )

        # PLANS
        self.stdout.write('Creating plans...')
        for name, amount in [
            ('Basic - 1 Modality', 120.00),
            ('Intermediate - 2 Modalities', 200.00),
            ('Full - Unlimited Modalities', 280.00),
        ]:
            Plan.objects.update_or_create(
                name=name,
                defaults={'amount': amount}
            )

        # ADMIN
        self.stdout.write('Creating admin user...')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@dojo.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('  admin created: user=admin / password=admin123'))
        else:
            self.stdout.write('  admin already exists.')

        self.stdout.write(self.style.SUCCESS('\nInitial data loaded!'))
        self.stdout.write('Access: http://127.0.0.1:8000/')
        self.stdout.write('Login: admin / admin123')