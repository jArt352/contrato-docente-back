"""
Script para crear los grupos (roles) del sistema
Ejecutar: python manage.py shell < create_groups.py
"""

from django.contrib.auth.models import Group

print("Creando grupos del sistema...")

GROUPS = [
    'ADJUDICATOR',
    'ADMIN',
    'EVALUATOR',
    'NEXUS',
    'TEACHER',
]

for group_name in GROUPS:
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f"   ✓ Creado: {group_name}")
    else:
        print(f"   - Ya existe: {group_name}")

print(f"\n✅ Grupos configurados: {Group.objects.count()} grupos en total")
print("\nGrupos disponibles:")
for group in Group.objects.all().order_by('name'):
    print(f"   - {group.name} (ID: {group.id})")
