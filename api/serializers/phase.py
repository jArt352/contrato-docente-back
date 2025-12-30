from rest_framework import serializers
from api.models import Phase, PhaseStage, PhaseAssignment, Modality, Level, CurricularArea
from django.utils import timezone


class PhaseStageSerializer(serializers.ModelSerializer):
    stage_type_display = serializers.CharField(source='get_stage_type_display', read_only=True)
    
    class Meta:
        model = PhaseStage
        fields = ['id', 'phase', 'stage_type', 'stage_type_display', 'start_date', 'end_date']
        read_only_fields = ['id']
    
    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError({
                    'end_date': 'La fecha de fin debe ser posterior a la fecha de inicio'
                })
        return data


class PhaseStageCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear etapas sin el campo phase"""
    
    class Meta:
        model = PhaseStage
        fields = ['stage_type', 'start_date', 'end_date']
    
    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError({
                    'end_date': 'La fecha de fin debe ser posterior a la fecha de inicio'
                })
        return data


class PhaseAssignmentSerializer(serializers.ModelSerializer):
    modality_name = serializers.CharField(source='modality.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    curricular_area_name = serializers.CharField(source='curricular_area.name', read_only=True, allow_null=True)
    
    class Meta:
        model = PhaseAssignment
        fields = [
            'id', 'phase', 'assignment_datetime', 
            'modality', 'modality_name',
            'level', 'level_name',
            'curricular_area', 'curricular_area_name',
            'notes'
        ]
        read_only_fields = ['id']


class PhaseAssignmentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear adjudicaciones sin el campo phase"""
    
    class Meta:
        model = PhaseAssignment
        fields = ['assignment_datetime', 'modality', 'level', 'curricular_area', 'notes']


class PhaseSerializer(serializers.ModelSerializer):
    stages = PhaseStageSerializer(many=True, read_only=True)
    assignments = PhaseAssignmentSerializer(many=True, read_only=True)
    
    stages_count = serializers.SerializerMethodField()
    assignments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Phase
        fields = [
            'id', 'name', 'description', 'year', 'is_active',
            'stages', 'assignments',
            'stages_count', 'assignments_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_stages_count(self, obj):
        return obj.stages.count()
    
    def get_assignments_count(self, obj):
        return obj.assignments.count()


class PhaseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer especial para crear una fase completa con etapas y adjudicaciones
    """
    stages = PhaseStageCreateSerializer(many=True)
    assignments = PhaseAssignmentCreateSerializer(many=True)
    
    class Meta:
        model = Phase
        fields = ['id', 'name', 'description', 'year', 'is_active', 'stages', 'assignments']
        read_only_fields = ['id']
    
    def validate(self, data):
        # Validar que no haya una fase activa
        if Phase.objects.filter(is_active=True).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Ya existe una fase activa. Desactívala antes de crear una nueva.'
            })
        
        # Validar que no haya una fase que ya va a empezar
        stages = data.get('stages', [])
        if stages:
            # Obtener la fecha de inicio más temprana
            earliest_start = min([stage['start_date'] for stage in stages if stage.get('start_date')])
            
            # Verificar si hay fases con fechas futuras que se superpongan
            existing_phases = Phase.objects.all()
            for phase in existing_phases:
                phase_stages = phase.stages.all()
                if phase_stages.exists():
                    # Obtener la última fecha de finalización de la fase existente
                    latest_end = max([s.end_date for s in phase_stages if s.end_date])
                    if latest_end and latest_end > timezone.now() and latest_end > earliest_start:
                        raise serializers.ValidationError({
                            'non_field_errors': f'La fase "{phase.name}" ya está programada y se superpone con las fechas seleccionadas.'
                        })
        
        # Validar que se incluyan todas las etapas requeridas
        required_stage_types = [
            'PUBLICATION',
            'ACCREDITATION',
            'TIE_EVALUATION',
            'PRELIMINARY_RESULTS',
            'CLAIMS',
            'CLAIM_RESOLUTION',
            'FINAL_RESULTS'
        ]
        
        stage_types_provided = [stage['stage_type'] for stage in stages]
        
        missing_stages = [st for st in required_stage_types if st not in stage_types_provided]
        if missing_stages:
            stage_names = [dict(PhaseStage.STAGE_TYPES).get(st) for st in missing_stages]
            raise serializers.ValidationError({
                'stages': f'Faltan las siguientes etapas: {", ".join(stage_names)}'
            })
        
        # Validar que haya al menos una adjudicación
        assignments = data.get('assignments', [])
        if not assignments:
            raise serializers.ValidationError({
                'assignments': 'Debe incluir al menos una adjudicación'
            })
        
        return data
    
    def create(self, validated_data):
        stages_data = validated_data.pop('stages', [])
        assignments_data = validated_data.pop('assignments', [])
        
        # Crear la fase
        phase = Phase.objects.create(**validated_data)
        
        # Crear las etapas
        for stage_data in stages_data:
            PhaseStage.objects.create(phase=phase, **stage_data)
        
        # Crear las adjudicaciones
        for assignment_data in assignments_data:
            PhaseAssignment.objects.create(phase=phase, **assignment_data)
        
        return phase
