from rest_framework import serializers
from api.models import EducationalInstitution, Vacancy, Modality, Level, CurricularArea, Phase


class EducationalInstitutionSerializer(serializers.ModelSerializer):
    modality_name = serializers.CharField(source='modality.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    
    class Meta:
        model = EducationalInstitution
        fields = ['id', 'code', 'name', 'modality', 'modality_name', 'level', 'level_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class VacancySerializer(serializers.ModelSerializer):
    ie_code = serializers.CharField(source='educational_institution.code', read_only=True)
    ie_name = serializers.CharField(source='educational_institution.name', read_only=True)
    educational_institution_name = serializers.CharField(source='educational_institution.name', read_only=True)
    phase_name = serializers.CharField(source='phase.name', read_only=True)
    curricular_area_name = serializers.CharField(source='curricular_area.name', read_only=True, allow_null=True)
    modality_name = serializers.CharField(source='educational_institution.modality.name', read_only=True)
    level_name = serializers.CharField(source='educational_institution.level.name', read_only=True)
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    vacancy_type_display = serializers.CharField(source='get_vacancy_type_display', read_only=True)
    vacancy_reason_display = serializers.CharField(source='get_vacancy_reason_display', read_only=True)
    
    class Meta:
        model = Vacancy
        fields = [
            'id', 'phase', 'phase_name', 'educational_institution', 'ie_code', 'ie_name', 'educational_institution_name',
            'modality_name', 'level_name', 'nexus_code', 'position', 'position_display', 'vacancy_type', 'vacancy_type_display',
            'vacancy_reason', 'vacancy_reason_display', 'curricular_area', 'curricular_area_name',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VacancyBulkCreateSerializer(serializers.Serializer):
    """
    Serializer para crear múltiples vacantes desde Excel
    """
    phase_id = serializers.IntegerField()
    vacancies = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )
    
    def validate_phase_id(self, value):
        try:
            Phase.objects.get(id=value)
        except Phase.DoesNotExist:
            raise serializers.ValidationError("La fase especificada no existe")
        return value
    
    def validate_vacancies(self, value):
        """
        Validar estructura de cada vacante en el listado
        Formato esperado:
        {
            "ie_code": "0123456",
            "ie_name": "IE 123",
            "modality": "EBR",
            "level": "Primaria",
            "nexus_code": "NEX001",
            "position": "DOCENTE",
            "vacancy_type": "ORGANICA",
            "vacancy_reason": "LICENCIA",
            "curricular_area": "Matemática" (opcional)
        }
        """
        if not value:
            raise serializers.ValidationError("Debe proporcionar al menos una vacante")
        
        required_fields = ['ie_code', 'ie_name', 'modality', 'level', 'nexus_code', 'position', 'vacancy_type', 'vacancy_reason']
        
        for idx, vacancy_data in enumerate(value):
            missing_fields = [field for field in required_fields if field not in vacancy_data]
            if missing_fields:
                raise serializers.ValidationError(
                    f"Fila {idx + 1}: Faltan campos requeridos: {', '.join(missing_fields)}"
                )
        
        return value
    
    def create(self, validated_data):
        phase_id = validated_data['phase_id']
        vacancies_data = validated_data['vacancies']
        
        phase = Phase.objects.get(id=phase_id)
        created_vacancies = []
        errors = []
        
        for idx, vacancy_data in enumerate(vacancies_data):
            try:
                # Buscar o crear IE
                modality = Modality.objects.filter(
                    abbreviature__iexact=vacancy_data['modality']
                ).first() or Modality.objects.filter(
                    name__iexact=vacancy_data['modality']
                ).first()
                
                if not modality:
                    errors.append(f"Fila {idx + 1}: Modalidad '{vacancy_data['modality']}' no encontrada")
                    continue
                
                level = Level.objects.filter(name__iexact=vacancy_data['level']).first()
                if not level:
                    errors.append(f"Fila {idx + 1}: Nivel '{vacancy_data['level']}' no encontrado")
                    continue
                
                ie, _ = EducationalInstitution.objects.get_or_create(
                    code=vacancy_data['ie_code'],
                    defaults={
                        'name': vacancy_data['ie_name'],
                        'modality': modality,
                        'level': level
                    }
                )
                
                # Buscar área curricular si se proporciona
                curricular_area = None
                area_name = vacancy_data.get('curricular_area')
                # Convertir NaN a None
                if area_name and not (isinstance(area_name, float) and pd.isna(area_name)):
                    curricular_area = CurricularArea.objects.filter(
                        name__iexact=str(area_name)
                    ).first()
                
                # Crear vacante
                vacancy = Vacancy.objects.create(
                    phase=phase,
                    educational_institution=ie,
                    nexus_code=vacancy_data['nexus_code'],
                    position=vacancy_data['position'].upper(),
                    vacancy_type=vacancy_data['vacancy_type'].upper(),
                    vacancy_reason=vacancy_data['vacancy_reason'].upper(),
                    curricular_area=curricular_area
                )
                created_vacancies.append(vacancy)
                
            except Exception as e:
                errors.append(f"Fila {idx + 1}: {str(e)}")
        
        return {
            'created_count': len(created_vacancies),
            'error_count': len(errors),
            'errors': errors,
            'vacancies': created_vacancies
        }
