from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Crea los grupos (roles) del sistema: ADJUDICATOR, ADMIN, EVALUATOR, NEXUS, TEACHER'

    def handle(self, *args, **options):
        GROUPS = [
            'ADJUDICATOR',
            'ADMIN',
            'EVALUATOR',
            'NEXUS',
            'TEACHER',
        ]

        self.stdout.write(self.style.WARNING('Creando grupos del sistema...'))

        created_count = 0
        existing_count = 0

        for group_name in GROUPS:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'   ✓ Creado: {group_name}'))
                created_count += 1
            else:
                self.stdout.write(f'   - Ya existe: {group_name}')
                existing_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n✅ Proceso completado:'))
        self.stdout.write(f'   - Grupos creados: {created_count}')
        self.stdout.write(f'   - Grupos existentes: {existing_count}')
        self.stdout.write(f'   - Total: {Group.objects.count()}')

        self.stdout.write('\nGrupos disponibles:')
        for group in Group.objects.all().order_by('name'):
            self.stdout.write(f'   - {group.name} (ID: {group.id})')
