"""
Script para crear usuarios de prueba con diferentes roles
Ejecutar: python create_test_users.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import Group as DjangoGroup
from api.models import Person, User, Group, TeacherProfile, EvaluatorProfile, Modality, Level, CurricularArea

print("=" * 70)
print("CREANDO USUARIOS DE PRUEBA")
print("=" * 70)

# 1. Crear grupos (roles) de Django Auth
print("\n1. Creando grupos de Django Auth...")
django_groups = {
    'ADMIN': None,
    'EVALUATOR': None,
    'TEACHER': None,
    'NEXUS': None,
    'ADJUDICATOR': None,
}

for group_name in django_groups.keys():
    group, created = DjangoGroup.objects.get_or_create(name=group_name)
    django_groups[group_name] = group
    print(f"   {'✓ Creado' if created else '- Existente'}: {group_name}")

# 2. Crear grupos personalizados (para el campo role)
print("\n2. Creando grupos personalizados...")
custom_groups = {}
for group_name in django_groups.keys():
    group, created = Group.objects.get_or_create(
        name=group_name,
        defaults={'description': f'Grupo de {group_name}'}
    )
    custom_groups[group_name] = group
    print(f"   {'✓ Creado' if created else '- Existente'}: {group_name}")

# 3. Obtener datos necesarios para perfiles
print("\n3. Obteniendo modalidades, niveles y áreas curriculares...")
modalities = list(Modality.objects.filter(is_active=True)[:3])
levels = list(Level.objects.filter(is_active=True)[:3])
areas = list(CurricularArea.objects.filter(is_active=True)[:5])

if not modalities:
    print("   ⚠ No hay modalidades. Creando básicas...")
    modalities = [
        Modality.objects.create(name="Educación Básica Regular", abbreviature="EBR", is_active=True),
        Modality.objects.create(name="Educación Básica Alternativa", abbreviature="EBA", is_active=True),
    ]

if not levels:
    print("   ⚠ No hay niveles. Creando básicos...")
    levels = [
        Level.objects.create(name="Inicial", is_active=True),
        Level.objects.create(name="Primaria", is_active=True),
        Level.objects.create(name="Secundaria", is_active=True),
    ]

if not areas:
    print("   ⚠ No hay áreas curriculares. Creando básicas...")
    areas = [
        CurricularArea.objects.create(name="Matemática", is_active=True),
        CurricularArea.objects.create(name="Comunicación", is_active=True),
        CurricularArea.objects.create(name="Ciencia y Tecnología", is_active=True),
        CurricularArea.objects.create(name="Ciencias Sociales", is_active=True),
        CurricularArea.objects.create(name="Inglés", is_active=True),
    ]

print(f"   ✓ {len(modalities)} modalidades, {len(levels)} niveles, {len(areas)} áreas")

# 4. Función para crear usuario
def create_user(username, first_name, paternal_surname, maternal_surname, dni, email, role_name, is_staff=False, is_superuser=False):
    """Crea una persona y su usuario asociado"""
    
    # Crear persona
    person, created = Person.objects.get_or_create(
        dni=dni,
        defaults={
            'first_name': first_name,
            'paternal_surname': paternal_surname,
            'maternal_surname': maternal_surname,
            'email': email,
        }
    )
    
    if created:
        print(f"   ✓ Persona creada: {person}")
    
    # Crear usuario
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'person': person,
            'email': email,
            'is_staff': is_staff,
            'is_superuser': is_superuser,
            'is_active': True,
            'role': custom_groups[role_name],
        }
    )
    
    if created:
        user.set_password('password123')  # Contraseña por defecto
        user.save()
        
        # Agregar al grupo de Django
        user.groups.add(django_groups[role_name])
        
        print(f"   ✓ Usuario creado: {username} ({role_name})")
    else:
        print(f"   - Usuario existente: {username}")
    
    return user

# 5. Crear ADMIN (1)
print("\n4. Creando ADMIN (1)...")
admin = create_user(
    username='admin',
    first_name='Carlos',
    paternal_surname='Administrador',
    maternal_surname='Sistema',
    dni='70000001',
    email='admin@ugel.gob.pe',
    role_name='ADMIN',
    is_staff=True,
    is_superuser=True
)

# 6. Crear EVALUATORS (3)
print("\n5. Creando EVALUATORS (3)...")
evaluators = []
evaluator_data = [
    ('evaluator1', 'María', 'Evaluadora', 'Gómez', '70000002', 'evaluator1@ugel.gob.pe'),
    ('evaluator2', 'Pedro', 'Calificador', 'López', '70000003', 'evaluator2@ugel.gob.pe'),
    ('evaluator3', 'Ana', 'Revisora', 'Martínez', '70000004', 'evaluator3@ugel.gob.pe'),
]

for username, first_name, paternal, maternal, dni, email in evaluator_data:
    user = create_user(username, first_name, paternal, maternal, dni, email, 'EVALUATOR', is_staff=True)
    evaluators.append(user)
    
    # Crear perfil de evaluador si no existe
    if not hasattr(user, 'evaluator_profile'):
        profile = EvaluatorProfile.objects.create(user=user)
        # Asignar modalidades, niveles y áreas
        profile.modalities.set(modalities[:2])  # Primeras 2 modalidades
        profile.levels.set(levels[:2])  # Primeros 2 niveles
        profile.curricular_areas.set(areas[:3])  # Primeras 3 áreas
        print(f"      → Perfil de evaluador creado")

# 7. Crear TEACHERS (5)
print("\n6. Creando TEACHERS (5)...")
teachers = []
teacher_data = [
    ('teacher1', 'Luis', 'Docente', 'Fernández', '70000005', 'teacher1@ugel.gob.pe'),
    ('teacher2', 'Rosa', 'Profesora', 'Ramírez', '70000006', 'teacher2@ugel.gob.pe'),
    ('teacher3', 'Jorge', 'Maestro', 'Torres', '70000007', 'teacher3@ugel.gob.pe'),
    ('teacher4', 'Carmen', 'Educadora', 'Vega', '70000008', 'teacher4@ugel.gob.pe'),
    ('teacher5', 'Ricardo', 'Instructor', 'Sánchez', '70000009', 'teacher5@ugel.gob.pe'),
]

for idx, (username, first_name, paternal, maternal, dni, email) in enumerate(teacher_data):
    user = create_user(username, first_name, paternal, maternal, dni, email, 'TEACHER')
    teachers.append(user)
    
    # Crear perfil de docente si no existe
    if not hasattr(user, 'teacher_profile'):
        # Asignar modalidad, nivel y área (rotando para variedad)
        modality = modalities[idx % len(modalities)]
        level = levels[idx % len(levels)]
        area = areas[idx % len(areas)]
        
        profile = TeacherProfile.objects.create(
            user=user,
            modality=modality,
            level=level,
            curricular_area=area
        )
        print(f"      → Perfil docente: {modality.abbreviature} - {level.name} - {area.name}")

# 8. Crear NEXUS (2)
print("\n7. Creando NEXUS (2)...")
nexus_data = [
    ('nexus1', 'Patricia', 'Coordinadora', 'Mendoza', '70000010', 'nexus1@ugel.gob.pe'),
    ('nexus2', 'Alberto', 'Enlace', 'Cruz', '70000011', 'nexus2@ugel.gob.pe'),
]

for username, first_name, paternal, maternal, dni, email in nexus_data:
    create_user(username, first_name, paternal, maternal, dni, email, 'NEXUS', is_staff=True)

# 9. Crear ADJUDICATORS (3)
print("\n8. Creando ADJUDICATORS (3)...")
adjudicator_data = [
    ('adjudicator1', 'Miguel', 'Adjudicador', 'Rojas', '70000012', 'adjudicator1@ugel.gob.pe'),
    ('adjudicator2', 'Lucía', 'Asignadora', 'Flores', '70000013', 'adjudicator2@ugel.gob.pe'),
    ('adjudicator3', 'Fernando', 'Gestor', 'Paredes', '70000014', 'adjudicator3@ugel.gob.pe'),
]

for username, first_name, paternal, maternal, dni, email in adjudicator_data:
    create_user(username, first_name, paternal, maternal, dni, email, 'ADJUDICATOR', is_staff=True)

# 10. Resumen final
print("\n" + "=" * 70)
print("RESUMEN DE USUARIOS CREADOS")
print("=" * 70)
print(f"Total de personas: {Person.objects.count()}")
print(f"Total de usuarios: {User.objects.count()}")
print(f"\nPor rol:")
for role_name in ['ADMIN', 'EVALUATOR', 'TEACHER', 'NEXUS', 'ADJUDICATOR']:
    count = User.objects.filter(role__name=role_name).count()
    print(f"   {role_name}: {count}")

print(f"\nPerfiles especiales:")
print(f"   Perfiles de Evaluador: {EvaluatorProfile.objects.count()}")
print(f"   Perfiles de Docente: {TeacherProfile.objects.count()}")

print("\n" + "=" * 70)
print("CREDENCIALES DE ACCESO")
print("=" * 70)
print("Todos los usuarios tienen la contraseña: password123")
print("\nEjemplos de login:")
print("   Admin:       admin / password123")
print("   Evaluador:   evaluator1 / password123")
print("   Docente:     teacher1 / password123")
print("   Nexus:       nexus1 / password123")
print("   Adjudicador: adjudicator1 / password123")
print("=" * 70)
