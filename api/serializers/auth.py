from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para login con JWT.
    Devuelve tokens y datos del usuario.
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Agregar datos del usuario al response
        user = self.user
        data['user'] = {
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
            data['user']['person'] = {
                'id': person.id,
                'first_name': person.first_name,
                'paternal_surname': person.paternal_surname,
                'maternal_surname': person.maternal_surname,
                'dni': person.dni,
                'email': person.email,
            }
            data['user']['full_name'] = f"{person.first_name} {person.paternal_surname} {person.maternal_surname}"
        
        # Agregar perfil de docente si existe
        if hasattr(user, 'teacher_profile'):
            profile = user.teacher_profile
            data['user']['teacher_profile'] = {
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
            data['user']['evaluator_profile'] = {
                'modalities': [{'id': m.id, 'name': m.name} for m in profile.modalities.all()],
                'levels': [{'id': l.id, 'name': l.name} for l in profile.levels.all()],
                'curricular_areas': [{'id': ca.id, 'name': ca.name} for ca in profile.curricular_areas.all()],
            }
        
        return data


class LoginSerializer(serializers.Serializer):
    """
    Serializer para documentar el endpoint de login.
    """
    username = serializers.CharField(
        required=True,
        help_text='Nombre de usuario'
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Contraseña'
    )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambiar la contraseña del usuario actual.
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Contraseña actual'
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Nueva contraseña'
    )
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Contraseña actual incorrecta')
        return value
    
    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('La contraseña debe tener al menos 8 caracteres')
        return value
