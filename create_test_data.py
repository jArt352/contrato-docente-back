"""
Script para crear datos de prueba en el sistema de prelaciones
Ejecutar: python manage.py shell < create_test_data.py
"""

from api.models import Modality, Level, CurricularArea, PrelationOrder, Prelation, PrelationRequirement

print("Creando datos de prueba...")

# 1. Crear Modalidades
print("\n1. Creando modalidades...")
modalities = [
    {"name": "Educación Básica Regular", "abbreviature": "EBR"},
    {"name": "Educación Básica Alternativa", "abbreviature": "EBA"},
    {"name": "Educación Básica Especial", "abbreviature": "EBE"},
]

for mod_data in modalities:
    modality, created = Modality.objects.get_or_create(
        abbreviature=mod_data["abbreviature"],
        defaults={"name": mod_data["name"], "is_active": True}
    )
    print(f"   {'Creada' if created else 'Existente'}: {modality.abbreviature} - {modality.name}")

# 2. Crear Niveles
print("\n2. Creando niveles...")
levels = ["Inicial", "Primaria", "Secundaria"]

for level_name in levels:
    level, created = Level.objects.get_or_create(
        name=level_name,
        defaults={"is_active": True}
    )
    print(f"   {'Creado' if created else 'Existente'}: {level.name}")

# 3. Crear Áreas Curriculares
print("\n3. Creando áreas curriculares...")
areas = [
    "Matemática",
    "Comunicación",
    "Ciencia y Tecnología",
    "Ciencias Sociales",
    "Inglés",
    "Arte y Cultura",
    "Educación Física",
    "Educación Religiosa",
    "Tutoría",
]

for area_name in areas:
    area, created = CurricularArea.objects.get_or_create(
        name=area_name,
        defaults={"is_active": True}
    )
    print(f"   {'Creada' if created else 'Existente'}: {area.name}")

# 4. Crear Órdenes de Prelación
print("\n4. Creando órdenes de prelación...")
orders = [
    "Primera Prelación",
    "Segunda Prelación",
    "Tercera Prelación",
    "Cuarta Prelación",
]

for order_name in orders:
    order, created = PrelationOrder.objects.get_or_create(name=order_name)
    print(f"   {'Creado' if created else 'Existente'}: {order.name}")

# 5. Crear Prelaciones de ejemplo
print("\n5. Creando prelaciones de ejemplo...")

# Obtener datos necesarios
ebr = Modality.objects.get(abbreviature="EBR")
inicial = Level.objects.get(name="Inicial")
primaria = Level.objects.get(name="Primaria")
secundaria = Level.objects.get(name="Secundaria")
matematica = CurricularArea.objects.get(name="Matemática")
comunicacion = CurricularArea.objects.get(name="Comunicación")
primera = PrelationOrder.objects.get(name="Primera Prelación")
segunda = PrelationOrder.objects.get(name="Segunda Prelación")

# Prelación 1: EBR Inicial - Primera
prelation1, created = Prelation.objects.get_or_create(
    modality=ebr,
    curricular_area=None,
    order=primera,
    defaults={
        "description": "Docentes con título pedagógico en Educación Inicial",
        "is_active": True
    }
)
if created:
    prelation1.level.add(inicial)
    print(f"   Creada: Prelación 1 - EBR Inicial - Primera")
    
    # Agregar requisitos - Grupo 1
    PrelationRequirement.objects.create(
        prelation=prelation1,
        text="Título profesional de profesor en Educación Inicial",
        logic_type="OR",
        group=1,
        is_active=True
    )
    PrelationRequirement.objects.create(
        prelation=prelation1,
        text="Título de licenciado en Educación Inicial",
        logic_type="OR",
        group=1,
        is_active=True
    )
    
    # Agregar requisitos - Grupo 2
    PrelationRequirement.objects.create(
        prelation=prelation1,
        text="Copia del DNI",
        logic_type="AND",
        group=2,
        is_active=True
    )
    PrelationRequirement.objects.create(
        prelation=prelation1,
        text="Declaración jurada de no tener impedimento",
        logic_type="AND",
        group=2,
        is_active=True
    )
    print("      - Requisitos agregados (2 grupos)")

# Prelación 2: EBR Secundaria Matemática - Primera
prelation2, created = Prelation.objects.get_or_create(
    modality=ebr,
    curricular_area=matematica,
    order=primera,
    defaults={
        "description": "Docentes con título en Matemática o Educación Secundaria especialidad Matemática",
        "is_active": True
    }
)
if created:
    prelation2.level.add(secundaria)
    print(f"   Creada: Prelación 2 - EBR Secundaria Matemática - Primera")
    
    # Agregar requisitos - Grupo 1
    PrelationRequirement.objects.create(
        prelation=prelation2,
        text="Título de profesor en Matemática",
        logic_type="OR",
        group=1,
        is_active=True
    )
    PrelationRequirement.objects.create(
        prelation=prelation2,
        text="Título en Educación Secundaria especialidad Matemática",
        logic_type="OR",
        group=1,
        is_active=True
    )
    PrelationRequirement.objects.create(
        prelation=prelation2,
        text="Título profesional de Matemático con estudios pedagógicos",
        logic_type="OR",
        group=1,
        is_active=True
    )
    
    # Agregar requisitos - Grupo 2
    PrelationRequirement.objects.create(
        prelation=prelation2,
        text="Constancia de habilitación profesional vigente",
        logic_type="AND",
        group=2,
        is_active=True
    )
    print("      - Requisitos agregados (2 grupos)")

# Prelación 3: EBR Primaria - Segunda
prelation3, created = Prelation.objects.get_or_create(
    modality=ebr,
    curricular_area=None,
    order=segunda,
    defaults={
        "description": "Profesionales con título pedagógico en otra especialidad con estudios de complementación",
        "is_active": True
    }
)
if created:
    prelation3.level.add(primaria)
    print(f"   Creada: Prelación 3 - EBR Primaria - Segunda")
    
    # Agregar requisitos - Grupo 1
    PrelationRequirement.objects.create(
        prelation=prelation3,
        text="Título pedagógico en cualquier especialidad",
        logic_type="AND",
        group=1,
        is_active=True
    )
    PrelationRequirement.objects.create(
        prelation=prelation3,
        text="Diploma de Segunda Especialidad en Educación Primaria",
        logic_type="AND",
        group=1,
        is_active=True
    )
    
    # Agregar requisitos - Grupo 2
    PrelationRequirement.objects.create(
        prelation=prelation3,
        text="Certificado de estudios de Segunda Especialidad (mínimo 1 año)",
        logic_type="OR",
        group=2,
        is_active=True
    )
    PrelationRequirement.objects.create(
        prelation=prelation3,
        text="Constancia de estudios concluidos",
        logic_type="OR",
        group=2,
        is_active=True
    )
    print("      - Requisitos agregados (2 grupos)")

print("\n✅ Datos de prueba creados exitosamente!")
print("\nResumen:")
print(f"   - Modalidades: {Modality.objects.count()}")
print(f"   - Niveles: {Level.objects.count()}")
print(f"   - Áreas Curriculares: {CurricularArea.objects.count()}")
print(f"   - Órdenes de Prelación: {PrelationOrder.objects.count()}")
print(f"   - Prelaciones: {Prelation.objects.count()}")
print(f"   - Requisitos: {PrelationRequirement.objects.count()}")
print("\nPuedes acceder a los datos en:")
print("   - Backend: http://localhost:8000/api/prelations/")
print("   - Frontend: http://localhost:3000/admin/prelaciones")
