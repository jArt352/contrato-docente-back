# Sistema de Autenticación y Gestión de Usuarios

## Descripción

Sistema completo de autenticación con usuarios, roles (grupos) y perfiles específicos para TEACHER y EVALUATOR.

## Grupos (Roles) del Sistema

El sistema maneja 5 grupos principales:

| Grupo | Descripción | Perfil Especial |
|-------|-------------|-----------------|
| **ADJUDICATOR** | Adjudicador | No |
| **ADMIN** | Administrador | No |
| **EVALUATOR** | Evaluador de documentos | ✅ Sí (múltiples asignaciones) |
| **NEXUS** | Personal de NEXUS | No |
| **TEACHER** | Docente | ✅ Sí (una asignación) |

## Modelos

### 1. User (Usuario)
Modelo personalizado que extiende `AbstractUser` de Django.

**Campos adicionales:**
- `person`: Relación 1:1 con Person
- `role`: ForeignKey a Group (rol del usuario)
- `is_active`: Estado del usuario
- `created_at`: Fecha de creación
- `updated_at`: Fecha de última actualización

### 2. TeacherProfile (Perfil de Docente)
Perfil específico para usuarios con rol TEACHER.

**Características:**
- **UN** solo usuario
- **UNA** modalidad
- **UN** nivel
- **UN** área curricular

**Campos:**
- `user`: OneToOne con User
- `modality`: ForeignKey a Modality
- `level`: ForeignKey a Level
- `curricular_area`: ForeignKey a CurricularArea

### 3. EvaluatorProfile (Perfil de Evaluador)
Perfil específico para usuarios con rol EVALUATOR.

**Características:**
- **UN** solo usuario
- **VARIAS** modalidades
- **VARIOS** niveles
- **VARIAS** áreas curriculares

**Campos:**
- `user`: OneToOne con User
- `modalities`: ManyToMany con Modality
- `levels`: ManyToMany con Level
- `curricular_areas`: ManyToMany con CurricularArea

## Endpoints API

### Grupos (Roles)

```
GET /api/auth/groups/
```
Lista todos los grupos del sistema.

**Permisos:** Usuarios autenticados

**Respuesta:**
```json
[
  {
    "id": 1,
    "name": "TEACHER",
    "user_count": 5
  },
  {
    "id": 2,
    "name": "EVALUATOR",
    "user_count": 3
  }
]
```

---

```
GET /api/auth/groups/{id}/
```
Detalle de un grupo específico.

---

### Usuarios

```
GET /api/auth/users/
```
Lista todos los usuarios con sus perfiles.

**Permisos:** Solo administradores

**Respuesta:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "jperez",
      "email": "jperez@ugel.gob.pe",
      "first_name": "Juan",
      "last_name": "Pérez",
      "person": {
        "id": 1,
        "first_name": "Juan",
        "paternal_surname": "Pérez",
        "maternal_surname": "García",
        "dni": "12345678",
        "email": "jperez@ugel.gob.pe"
      },
      "role": 1,
      "role_name": "TEACHER",
      "full_name": "Juan Pérez García",
      "teacher_profile": {
        "modality": 1,
        "modality_name": "Educación Básica Regular",
        "level": 2,
        "level_name": "Primaria",
        "curricular_area": 1,
        "curricular_area_name": "Matemática"
      },
      "evaluator_profile": null,
      "is_active": true,
      "is_staff": false,
      "is_superuser": false,
      "created_at": "2025-12-26T10:00:00Z",
      "updated_at": "2025-12-26T10:00:00Z"
    }
  ]
}
```

---

```
POST /api/auth/users/
```
Crear un nuevo usuario con Person y perfil.

**Permisos:** Solo administradores

**Body para TEACHER:**
```json
{
  "username": "jperez",
  "email": "jperez@ugel.gob.pe",
  "first_name": "Juan",
  "last_name": "Pérez",
  "password": "Password123!",
  "role": 1,
  "is_active": true,
  "person_first_name": "Juan",
  "person_paternal_surname": "Pérez",
  "person_maternal_surname": "García",
  "person_dni": "12345678",
  "person_email": "jperez@ugel.gob.pe",
  "teacher_modality": 1,
  "teacher_level": 2,
  "teacher_curricular_area": 1
}
```

**Body para EVALUATOR:**
```json
{
  "username": "mlopez",
  "email": "mlopez@ugel.gob.pe",
  "first_name": "María",
  "last_name": "López",
  "password": "Password123!",
  "role": 3,
  "is_active": true,
  "person_first_name": "María",
  "person_paternal_surname": "López",
  "person_maternal_surname": "Sánchez",
  "person_dni": "87654321",
  "person_email": "mlopez@ugel.gob.pe",
  "evaluator_modalities": [1, 2],
  "evaluator_levels": [1, 2, 3],
  "evaluator_curricular_areas": [1, 2, 3, 4]
}
```

**Body para otros roles (ADMIN, NEXUS, ADJUDICATOR):**
```json
{
  "username": "admin",
  "email": "admin@ugel.gob.pe",
  "first_name": "Admin",
  "last_name": "Sistema",
  "password": "Password123!",
  "role": 2,
  "is_active": true,
  "person_first_name": "Admin",
  "person_paternal_surname": "Sistema",
  "person_maternal_surname": "UGEL",
  "person_dni": "00000000",
  "person_email": "admin@ugel.gob.pe"
}
```

---

```
GET /api/auth/users/{id}/
```
Obtener detalle de un usuario específico.

**Permisos:** Solo administradores

---

```
PUT/PATCH /api/auth/users/{id}/
```
Actualizar un usuario.

**Permisos:** Solo administradores

---

```
DELETE /api/auth/users/{id}/
```
Eliminar un usuario.

**Permisos:** Solo administradores

---

```
GET /api/auth/users/me/
```
Obtener información del usuario autenticado.

**Permisos:** Usuarios autenticados

**Respuesta:**
```json
{
  "id": 1,
  "username": "jperez",
  "email": "jperez@ugel.gob.pe",
  "role_name": "TEACHER",
  "full_name": "Juan Pérez García",
  "teacher_profile": {...}
}
```

---

```
GET /api/auth/users/by_role/?role=TEACHER
```
Filtrar usuarios por rol.

**Permisos:** Solo administradores

**Parámetros:**
- `role`: Nombre del rol (TEACHER, EVALUATOR, ADMIN, NEXUS, ADJUDICATOR)

---

```
POST /api/auth/users/{id}/change_password/
```
Cambiar contraseña de un usuario.

**Permisos:** Solo administradores

**Body:**
```json
{
  "password": "NewPassword123!"
}
```

## Instalación y Configuración

### 1. Crear migraciones

Debido al cambio del modelo User, necesitas crear nuevas migraciones:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Crear grupos del sistema

Usa el management command creado:

```bash
python manage.py create_groups
```

O ejecuta el script:

```bash
python manage.py shell < create_groups.py
```

### 3. Crear superusuario

```bash
python manage.py createsuperuser
```

### 4. Crear datos de prueba

Primero asegúrate de tener modalidades, niveles y áreas curriculares:

```bash
python manage.py shell < create_test_data.py
```

## Ejemplos de Uso

### Crear un docente (TEACHER)

```bash
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "docente1",
    "email": "docente1@ugel.gob.pe",
    "password": "Pass123!",
    "role": 1,
    "person_first_name": "María",
    "person_paternal_surname": "González",
    "person_maternal_surname": "Rodríguez",
    "person_dni": "45678901",
    "person_email": "docente1@ugel.gob.pe",
    "teacher_modality": 1,
    "teacher_level": 2,
    "teacher_curricular_area": 1
  }'
```

### Crear un evaluador (EVALUATOR)

```bash
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "evaluador1",
    "email": "evaluador1@ugel.gob.pe",
    "password": "Pass123!",
    "role": 3,
    "person_first_name": "Carlos",
    "person_paternal_surname": "Ramírez",
    "person_maternal_surname": "Torres",
    "person_dni": "56789012",
    "person_email": "evaluador1@ugel.gob.pe",
    "evaluator_modalities": [1, 2],
    "evaluator_levels": [1, 2, 3],
    "evaluator_curricular_areas": [1, 2, 3]
  }'
```

### Listar usuarios por rol

```bash
curl http://localhost:8000/api/auth/users/by_role/?role=TEACHER \
  -H "Authorization: Bearer <token>"
```

### Obtener mi información

```bash
curl http://localhost:8000/api/auth/users/me/ \
  -H "Authorization: Bearer <token>"
```

## Validaciones

### Para TEACHER:
- ✅ Debe tener `teacher_modality`
- ✅ Debe tener `teacher_level`
- ✅ Debe tener `teacher_curricular_area`
- ✅ Solo puede tener UN valor de cada uno

### Para EVALUATOR:
- ✅ Debe tener `evaluator_modalities` (lista)
- ✅ Debe tener `evaluator_levels` (lista)
- ✅ Debe tener `evaluator_curricular_areas` (lista)
- ✅ Puede tener VARIOS valores de cada uno

### Para otros roles:
- ✅ No requieren perfiles especiales
- ✅ No se crean TeacherProfile ni EvaluatorProfile

## Estructura de Archivos

```
api/
├── models.py                      # User, TeacherProfile, EvaluatorProfile
├── serializers/
│   └── user.py                   # Serializers de auth
├── views/
│   └── user.py                   # ViewSets de auth
├── management/
│   └── commands/
│       └── create_groups.py      # Command para crear grupos
└── router.py                      # URLs configuradas
```

## Permisos

| Acción | Endpoint | Permiso |
|--------|----------|---------|
| Listar grupos | GET /auth/groups/ | IsAuthenticated |
| Ver grupo | GET /auth/groups/{id}/ | IsAuthenticated |
| Listar usuarios | GET /auth/users/ | IsAdminUser |
| Crear usuario | POST /auth/users/ | IsAdminUser |
| Ver usuario | GET /auth/users/{id}/ | IsAdminUser |
| Actualizar usuario | PUT/PATCH /auth/users/{id}/ | IsAdminUser |
| Eliminar usuario | DELETE /auth/users/{id}/ | IsAdminUser |
| Ver mi perfil | GET /auth/users/me/ | IsAuthenticated |
| Filtrar por rol | GET /auth/users/by_role/ | IsAdminUser |
| Cambiar contraseña | POST /auth/users/{id}/change_password/ | IsAdminUser |

## Notas Importantes

1. **Person único por DNI:** Si el DNI ya existe, se vincula al Person existente
2. **Cambio de rol:** Al cambiar el rol de un usuario, se eliminan los perfiles anteriores y se crean los nuevos según corresponda
3. **Perfiles automáticos:** Los perfiles se crean automáticamente al crear/actualizar usuarios con roles TEACHER o EVALUATOR
4. **Validación de datos:** El sistema valida que TEACHER y EVALUATOR tengan las asignaciones correspondientes

## Soporte

Para más información, revisa:
- [models.py](../api/models.py) - Modelos del sistema
- [serializers/user.py](../api/serializers/user.py) - Serializers
- [views/user.py](../api/views/user.py) - Views y lógica
