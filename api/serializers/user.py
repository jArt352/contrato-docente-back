from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from api.models import User, Person, TeacherProfile, EvaluatorProfile, Modality, Level, CurricularArea


class GroupSerializer(serializers.ModelSerializer):
    """Serializer para grupos de Django"""
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'user_count']
    
    def get_user_count(self, obj):
        return obj.users.count()


class PersonSerializer(serializers.ModelSerializer):
    """Serializer para Person"""
    class Meta:
        model = Person
        fields = ['id', 'first_name', 'paternal_surname', 'maternal_surname', 'dni', 'email']


class TeacherProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil de docente"""
    modality_name = serializers.CharField(source='modality.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    curricular_area_name = serializers.CharField(source='curricular_area.name', read_only=True)
    
    class Meta:
        model = TeacherProfile
        fields = [
            'modality', 'modality_name',
            'level', 'level_name',
            'curricular_area', 'curricular_area_name'
        ]


class EvaluatorProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil de evaluador"""
    modality_names = serializers.SerializerMethodField()
    level_names = serializers.SerializerMethodField()
    curricular_area_names = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluatorProfile
        fields = [
            'modalities', 'modality_names',
            'levels', 'level_names',
            'curricular_areas', 'curricular_area_names'
        ]
    
    def get_modality_names(self, obj):
        return [m.name for m in obj.modalities.all()]
    
    def get_level_names(self, obj):
        return [l.name for l in obj.levels.all()]
    
    def get_curricular_area_names(self, obj):
        return [ca.name for ca in obj.curricular_areas.all()]


class UserSerializer(serializers.ModelSerializer):
    """Serializer para listar usuarios"""
    person = PersonSerializer(read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    teacher_profile = TeacherProfileSerializer(read_only=True)
    evaluator_profile = EvaluatorProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'person', 'role', 'role_name', 'full_name',
            'teacher_profile', 'evaluator_profile',
            'is_active', 'is_staff', 'is_superuser',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios con Person y perfiles"""
    # Person data
    person_first_name = serializers.CharField(write_only=True)
    person_paternal_surname = serializers.CharField(write_only=True)
    person_maternal_surname = serializers.CharField(write_only=True)
    person_dni = serializers.CharField(write_only=True)
    person_email = serializers.EmailField(write_only=True)
    
    # Password
    password = serializers.CharField(write_only=True, required=True)
    
    # Teacher profile (solo si role es TEACHER)
    teacher_modality = serializers.PrimaryKeyRelatedField(
        queryset=Modality.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    teacher_level = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    teacher_curricular_area = serializers.PrimaryKeyRelatedField(
        queryset=CurricularArea.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Evaluator profile (solo si role es EVALUATOR)
    evaluator_modalities = serializers.PrimaryKeyRelatedField(
        queryset=Modality.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    evaluator_levels = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    evaluator_curricular_areas = serializers.PrimaryKeyRelatedField(
        queryset=CurricularArea.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password',
            'role', 'is_active',
            # Person fields
            'person_first_name', 'person_paternal_surname', 'person_maternal_surname',
            'person_dni', 'person_email',
            # Teacher profile fields
            'teacher_modality', 'teacher_level', 'teacher_curricular_area',
            # Evaluator profile fields
            'evaluator_modalities', 'evaluator_levels', 'evaluator_curricular_areas'
        ]
    
    def validate(self, data):
        """Validar que teacher y evaluator tengan los datos necesarios"""
        role = data.get('role')
        
        if role:
            role_name = role.name.upper()
            
            # Validar TEACHER
            if role_name == 'TEACHER':
                if not all([
                    data.get('teacher_modality'),
                    data.get('teacher_level'),
                    data.get('teacher_curricular_area')
                ]):
                    raise serializers.ValidationError(
                        "Los docentes (TEACHER) deben tener asignados modalidad, nivel y área curricular."
                    )
            
            # Validar EVALUATOR
            elif role_name == 'EVALUATOR':
                if not all([
                    data.get('evaluator_modalities'),
                    data.get('evaluator_levels'),
                    data.get('evaluator_curricular_areas')
                ]):
                    raise serializers.ValidationError(
                        "Los evaluadores (EVALUATOR) deben tener asignados modalidades, niveles y áreas curriculares."
                    )
        
        return data
    
    def create(self, validated_data):
        # Extraer datos de Person
        person_data = {
            'first_name': validated_data.pop('person_first_name'),
            'paternal_surname': validated_data.pop('person_paternal_surname'),
            'maternal_surname': validated_data.pop('person_maternal_surname'),
            'dni': validated_data.pop('person_dni'),
            'email': validated_data.pop('person_email'),
        }
        
        # Extraer datos de Teacher profile
        teacher_modality = validated_data.pop('teacher_modality', None)
        teacher_level = validated_data.pop('teacher_level', None)
        teacher_curricular_area = validated_data.pop('teacher_curricular_area', None)
        
        # Extraer datos de Evaluator profile
        evaluator_modalities = validated_data.pop('evaluator_modalities', [])
        evaluator_levels = validated_data.pop('evaluator_levels', [])
        evaluator_curricular_areas = validated_data.pop('evaluator_curricular_areas', [])
        
        # Hash password
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        
        # Crear o obtener Person
        person, created = Person.objects.get_or_create(
            dni=person_data['dni'],
            defaults=person_data
        )
        
        # Crear User
        user = User.objects.create(person=person, **validated_data)
        
        # Crear perfil según el rol
        if user.role:
            role_name = user.role.name.upper()
            
            if role_name == 'TEACHER' and all([teacher_modality, teacher_level, teacher_curricular_area]):
                TeacherProfile.objects.create(
                    user=user,
                    modality=teacher_modality,
                    level=teacher_level,
                    curricular_area=teacher_curricular_area
                )
            
            elif role_name == 'EVALUATOR':
                evaluator_profile = EvaluatorProfile.objects.create(user=user)
                if evaluator_modalities:
                    evaluator_profile.modalities.set(evaluator_modalities)
                if evaluator_levels:
                    evaluator_profile.levels.set(evaluator_levels)
                if evaluator_curricular_areas:
                    evaluator_profile.curricular_areas.set(evaluator_curricular_areas)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar usuarios"""
    # Teacher profile
    teacher_modality = serializers.PrimaryKeyRelatedField(
        queryset=Modality.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    teacher_level = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    teacher_curricular_area = serializers.PrimaryKeyRelatedField(
        queryset=CurricularArea.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Evaluator profile
    evaluator_modalities = serializers.PrimaryKeyRelatedField(
        queryset=Modality.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    evaluator_levels = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    evaluator_curricular_areas = serializers.PrimaryKeyRelatedField(
        queryset=CurricularArea.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'password',
            'teacher_modality', 'teacher_level', 'teacher_curricular_area',
            'evaluator_modalities', 'evaluator_levels', 'evaluator_curricular_areas'
        ]
    
    def update(self, instance, validated_data):
        # Extraer password si existe
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        
        # Extraer datos de perfiles
        teacher_modality = validated_data.pop('teacher_modality', None)
        teacher_level = validated_data.pop('teacher_level', None)
        teacher_curricular_area = validated_data.pop('teacher_curricular_area', None)
        
        evaluator_modalities = validated_data.pop('evaluator_modalities', None)
        evaluator_levels = validated_data.pop('evaluator_levels', None)
        evaluator_curricular_areas = validated_data.pop('evaluator_curricular_areas', None)
        
        # Actualizar User
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar o crear perfiles según el rol
        if instance.role:
            role_name = instance.role.name.upper()
            
            if role_name == 'TEACHER':
                # Eliminar evaluator profile si existe
                if hasattr(instance, 'evaluator_profile'):
                    instance.evaluator_profile.delete()
                
                # Actualizar o crear teacher profile
                if all([teacher_modality, teacher_level, teacher_curricular_area]):
                    TeacherProfile.objects.update_or_create(
                        user=instance,
                        defaults={
                            'modality': teacher_modality,
                            'level': teacher_level,
                            'curricular_area': teacher_curricular_area
                        }
                    )
            
            elif role_name == 'EVALUATOR':
                # Eliminar teacher profile si existe
                if hasattr(instance, 'teacher_profile'):
                    instance.teacher_profile.delete()
                
                # Actualizar o crear evaluator profile
                evaluator_profile, created = EvaluatorProfile.objects.get_or_create(user=instance)
                if evaluator_modalities is not None:
                    evaluator_profile.modalities.set(evaluator_modalities)
                if evaluator_levels is not None:
                    evaluator_profile.levels.set(evaluator_levels)
                if evaluator_curricular_areas is not None:
                    evaluator_profile.curricular_areas.set(evaluator_curricular_areas)
            
            else:
                # Otros roles: eliminar ambos perfiles
                if hasattr(instance, 'teacher_profile'):
                    instance.teacher_profile.delete()
                if hasattr(instance, 'evaluator_profile'):
                    instance.evaluator_profile.delete()
        
        return instance
