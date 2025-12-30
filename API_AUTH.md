# Endpoints de Autenticación

## Login

### POST `/api/auth/login/`

Autenticar usuario y obtener tokens JWT.

**Permisos:** Público (AllowAny)

**Body:**
```json
{
  "username": "jperez",
  "password": "Password123!"
}
```

**Respuesta exitosa (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "jperez",
    "email": "jperez@ugel.gob.pe",
    "first_name": "Juan",
    "last_name": "Pérez",
    "role": "TEACHER",
    "role_id": 1,
    "is_active": true,
    "is_staff": false,
    "person": {
      "id": 1,
      "first_name": "Juan",
      "paternal_surname": "Pérez",
      "maternal_surname": "García",
      "dni": "12345678",
      "email": "jperez@ugel.gob.pe"
    },
    "full_name": "Juan Pérez García",
    "teacher_profile": {
      "modality": 1,
      "modality_name": "Educación Básica Regular",
      "level": 2,
      "level_name": "Primaria",
      "curricular_area": 1,
      "curricular_area_name": "Matemática"
    }
  }
}
```

**Respuesta error (401):**
```json
{
  "detail": "No active account found with the given credentials"
}
```

**Ejemplo cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jperez",
    "password": "Password123!"
  }'
```

---

## Refresh Token

### POST `/api/auth/refresh/`

Refrescar el access token usando el refresh token.

**Permisos:** Público (AllowAny)

**Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Respuesta exitosa (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Ejemplo cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

---

## Mi Perfil

### GET `/api/auth/me/`

Obtener información del usuario autenticado.

**Permisos:** IsAuthenticated

**Headers:**
```
Authorization: Bearer <access_token>
```

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "username": "jperez",
  "email": "jperez@ugel.gob.pe",
  "first_name": "Juan",
  "last_name": "Pérez",
  "role": "TEACHER",
  "role_id": 1,
  "is_active": true,
  "is_staff": false,
  "person": {
    "id": 1,
    "first_name": "Juan",
    "paternal_surname": "Pérez",
    "maternal_surname": "García",
    "dni": "12345678",
    "email": "jperez@ugel.gob.pe"
  },
  "full_name": "Juan Pérez García",
  "teacher_profile": {
    "modality": 1,
    "modality_name": "Educación Básica Regular",
    "level": 2,
    "level_name": "Primaria",
    "curricular_area": 1,
    "curricular_area_name": "Matemática"
  }
}
```

**Ejemplo cURL:**
```bash
curl http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## Cambiar Contraseña

### POST `/api/auth/change-password/`

Cambiar la contraseña del usuario autenticado.

**Permisos:** IsAuthenticated

**Headers:**
```
Authorization: Bearer <access_token>
```

**Body:**
```json
{
  "old_password": "Password123!",
  "new_password": "NewPassword456!"
}
```

**Respuesta exitosa (200):**
```json
{
  "message": "Contraseña actualizada correctamente"
}
```

**Respuesta error (400):**
```json
{
  "old_password": ["Contraseña actual incorrecta"]
}
```

O:

```json
{
  "new_password": ["La contraseña debe tener al menos 8 caracteres"]
}
```

**Ejemplo cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/change-password/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "Password123!",
    "new_password": "NewPassword456!"
  }'
```

---

## Flujo de Autenticación

### 1. Login
```
POST /api/auth/login/
Body: { username, password }
→ Response: { access, refresh, user }
```

### 2. Usar el Access Token
```
Agregar header en cada request:
Authorization: Bearer <access_token>
```

### 3. Cuando el Access Token expire (1 día)
```
POST /api/auth/refresh/
Body: { refresh }
→ Response: { access }
```

### 4. El Refresh Token expira después de 7 días
```
Usuario debe hacer login nuevamente
```

---

## Configuración JWT (settings.py)

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
```

---

## Ejemplo de Uso Completo

### 1. Login
```javascript
const response = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'jperez',
    password: 'Password123!'
  })
});

const data = await response.json();
// Guardar tokens
localStorage.setItem('access_token', data.access);
localStorage.setItem('refresh_token', data.refresh);
localStorage.setItem('user', JSON.stringify(data.user));
```

### 2. Request con autenticación
```javascript
const accessToken = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/api/prelations/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  }
});
```

### 3. Refrescar token
```javascript
const refreshToken = localStorage.getItem('refresh_token');

const response = await fetch('http://localhost:8000/api/auth/refresh/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    refresh: refreshToken
  })
});

const data = await response.json();
localStorage.setItem('access_token', data.access);
```

### 4. Logout
```javascript
// Simplemente eliminar los tokens
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
localStorage.removeItem('user');
```

---

## Respuestas según el Rol

### TEACHER
```json
{
  "user": {
    "role": "TEACHER",
    "teacher_profile": {
      "modality": 1,
      "level": 2,
      "curricular_area": 1
    }
  }
}
```

### EVALUATOR
```json
{
  "user": {
    "role": "EVALUATOR",
    "evaluator_profile": {
      "modalities": [{"id": 1, "name": "EBR"}, {"id": 2, "name": "EBA"}],
      "levels": [{"id": 1, "name": "Inicial"}, {"id": 2, "name": "Primaria"}],
      "curricular_areas": [{"id": 1, "name": "Matemática"}]
    }
  }
}
```

### ADMIN / ADJUDICATOR / NEXUS
```json
{
  "user": {
    "role": "ADMIN",
    "is_staff": true
  }
}
```

---

## Manejo de Errores

| Código | Descripción |
|--------|-------------|
| 200 | OK |
| 400 | Bad Request (datos inválidos) |
| 401 | Unauthorized (credenciales inválidas o token expirado) |
| 403 | Forbidden (sin permisos) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Próximos Pasos

1. **Migrar la base de datos:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Crear los grupos:**
   ```bash
   python manage.py create_groups
   ```

3. **Crear un usuario de prueba:**
   ```bash
   python manage.py createsuperuser
   ```

4. **Probar el login:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password"}'
   ```
