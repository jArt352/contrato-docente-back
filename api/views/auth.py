from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from ..serializers.auth import (
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    ChangePasswordSerializer
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para login con JWT.
    
    POST /api/auth/login/
    
    Body:
    {
        "username": "user",
        "password": "password"
    }
    
    Response:
    {
        "access": "token",
        "refresh": "token",
        "user": {
            "id": 1,
            "username": "user",
            "email": "user@example.com",
            "first_name": "Name",
            "last_name": "Lastname",
            "role": "TEACHER",
            "role_id": 1,
            "is_active": true,
            "person": {...},
            "teacher_profile": {...}
        }
    }
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Cambiar contraseña del usuario autenticado.
    
    POST /api/auth/change-password/
    
    Body:
    {
        "old_password": "oldpass",
        "new_password": "newpass"
    }
    """
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Contraseña actualizada correctamente'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Obtener información del usuario autenticado.
    
    GET /api/auth/me/
    
    Response:
    {
        "id": 1,
        "username": "user",
        "email": "user@example.com",
        "role": "TEACHER",
        "role_id": 1,
        "full_name": "Name Lastname",
        "person": {...},
        "teacher_profile": {...}
    }
    """
    user = request.user
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role.name if user.role else None,
        'role_id': user.role.id if user.role else None,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
    }
    
    # Agregar información de Person si existe
    if hasattr(user, 'person') and user.person:
        person = user.person
        data['person'] = {
            'id': person.id,
            'first_name': person.first_name,
            'paternal_surname': person.paternal_surname,
            'maternal_surname': person.maternal_surname,
            'dni': person.dni,
            'email': person.email,
        }
        data['full_name'] = f"{person.first_name} {person.paternal_surname} {person.maternal_surname}"
    
    # Agregar perfil de docente si existe
    if hasattr(user, 'teacher_profile'):
        profile = user.teacher_profile
        data['teacher_profile'] = {
            'modality': profile.modality.id,
            'modality_name': profile.modality.name,
            'level': profile.level.id,
            'level_name': profile.level.name,
            'curricular_area': profile.curricular_area.id,
            'curricular_area_name': profile.curricular_area.name,
        }
    
    # Agregar perfil de evaluador si existe
    if hasattr(user, 'evaluator_profile'):
        profile = user.evaluator_profile
        data['evaluator_profile'] = {
            'modalities': [{'id': m.id, 'name': m.name} for m in profile.modalities.all()],
            'levels': [{'id': l.id, 'name': l.name} for l in profile.levels.all()],
            'curricular_areas': [{'id': ca.id, 'name': ca.name} for ca in profile.curricular_areas.all()],
        }
    
    return Response(data, status=status.HTTP_200_OK)
