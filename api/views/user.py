from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from django.contrib.auth.models import Group
from api.models import User
from api.serializers.user import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer, GroupSerializer
)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar grupos (roles) del sistema.
    Solo lectura para admins.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]
    
    def get_permissions(self):
        """Permitir lectura a usuarios autenticados"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de usuarios.
    Incluye creación con Person y perfiles específicos.
    """
    queryset = User.objects.select_related(
        'person', 'role', 'teacher_profile', 'evaluator_profile'
    ).prefetch_related(
        'teacher_profile__modality',
        'teacher_profile__level',
        'teacher_profile__curricular_area',
        'evaluator_profile__modalities',
        'evaluator_profile__levels',
        'evaluator_profile__curricular_areas'
    ).order_by('-created_at')
    
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Permitir que los usuarios vean su propio perfil"""
        if self.action == 'me':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Obtener información del usuario autenticado"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def by_role(self, request):
        """Filtrar usuarios por rol"""
        role_name = request.query_params.get('role', None)
        if role_name:
            users = self.queryset.filter(role__name__iexact=role_name)
        else:
            users = self.queryset
        
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def change_password(self, request, pk=None):
        """Cambiar contraseña de un usuario"""
        user = self.get_object()
        password = request.data.get('password')
        
        if not password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth.hashers import make_password
        user.password = make_password(password)
        user.save()
        
        return Response({'message': 'Password changed successfully'})
