# --- Person Document Model ---
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    paternal_surname = models.CharField(max_length=30)
    maternal_surname = models.CharField(max_length=30)
    dni= models.CharField(max_length=8, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.paternal_surname} {self.maternal_surname}"

class Modality(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviature = models.CharField(max_length=45, unique=True, null=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.abbreviature} - {self.name}"

class Level(models.Model):
    name = models.CharField(max_length=100, unique=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class CurricularArea(models.Model):
    name = models.CharField(max_length=100, unique=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class PrelationOrder(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
class Prelation(models.Model):
    modality = models.ForeignKey('Modality', on_delete=models.PROTECT, related_name='prelations')
    level = models.ManyToManyField('Level', related_name='prelations')
    curricular_area = models.ForeignKey('CurricularArea', on_delete=models.PROTECT, related_name='prelations', null=True)
    order = models.ForeignKey('PrelationOrder', on_delete=models.PROTECT, related_name='prelations')
    description = models.TextField()

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('modality', 'curricular_area', 'order')

    def __str__(self):
        levels = ', '.join([l.name for l in self.level.all()])
        curricular_area_name = self.curricular_area.name if self.curricular_area else 'N/A'
        return f"ID:{self.id} - {self.order.name} - {self.modality.name} - {levels} - {curricular_area_name}"

class PrelationRequirement(models.Model):
    prelation = models.ForeignKey('Prelation', related_name='requirements', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    logic_type = models.CharField(max_length=3, choices=[('AND', 'Y'), ('OR', 'O')], default='AND')
    group = models.IntegerField(default=1)
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.logic_type} - {self.text} (Group {self.group})"

class InstitutionType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Dependency(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ServiceModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Institution(models.Model):
    name = models.CharField(max_length=255)
    modality = models.ForeignKey(Modality, on_delete=models.PROTECT, related_name='institutions')
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='institutions')
    type = models.ForeignKey(InstitutionType, on_delete=models.PROTECT, related_name='institutions')
    dependency = models.ForeignKey(Dependency, on_delete=models.PROTECT, related_name='institutions')
    service_model = models.ForeignKey(ServiceModel, on_delete=models.PROTECT, related_name='institutions')

    def __str__(self):
        return self.name

class Vacancy(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='vacancies')
    nexus_code = models.CharField(max_length=50, unique=True)
    position = models.CharField(max_length=100)
    workday = models.CharField(max_length=100)
    curricular_area = models.CharField(max_length=100)
    vacancy_type = models.CharField(max_length=100)
    vacancy_reason = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nexus_code} - {self.position} - {self.institution.name}"

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Subgroup(models.Model):
    group = models.ForeignKey('Group', related_name='subgroups', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('group', 'name')

    def __str__(self):
        return f"{self.name} ({self.group.name})"

class MandatoryDocument(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='mandatory_documents/', blank=True, null=True)

    def __str__(self):
        return self.name

class PhaseType(models.TextChoices):
    PUN = 'PUN', 'Fase 2: Prueba Nacional'
    EP = 'EP', 'Fase 3: Evaluación por Expedientes'

class StageType(models.TextChoices):
    RequirementsVerification = 'RequirementsVerification', 'Verificación de Requisitos'
    PreliminaryEvaluation = 'PreliminaryEvaluation', 'Evaluación Preliminar'
    PreliminaryResults= 'PreliminaryResults', 'Publicación de Resultados'
    ClaimsPeriod = 'ClaimsPeriod', 'Periodo de Reclamos'
    CorrectsClaims = 'CorrectsClaims', 'Corrección de Reclamos'
    FinalResults = 'FinalResults', 'Publicación de Resultados Finales'
    Adjudication = 'Adjudication', 'Adjudicación'

class ContractingProcess(models.Model):
    Name = models.CharField(max_length=100)
    year = models.PositiveIntegerField(unique=True)
    is_active = models.BooleanField(default=False)

    #Comproar si ya se activó la fase de evaluación por expedientes
    files_evaluation_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.Name

class Stage(models.Model):
    stage = models.ForeignKey(ContractingProcess, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=190)
    type = models.CharField(max_length=30, choices=StageType.choices)
    order = models.PositiveIntegerField()

    #---Fechas nullables---
    # Clave: Son null=True porque al crear el periodo, las etapas de la Fase 2
    # existen estructuralmente pero NO temporalmente.

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    is_qualifiable = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.stage.get_type_display()})"
    
    def esta_programada(self):
        """Retorna True si la etapa ya tiene fechas definidas."""
        return self.start_date is not None and self.end_date is not None
    
class ConvocatoriaAdjudicacion(models.Model):
    """
    Las 'n' convocatorias que ocurren DENTRO de la etapa de Adjudicación.
    Se crean dinámicamente conforme avanza el proceso.
    """
    stage = models.ForeignKey(Stage, related_name='convocatorias', on_delete=models.CASCADE)
    numero_convocatoria = models.PositiveIntegerField(help_text="1, 2, 3...")
    nombre = models.CharField(max_length=100, help_text="Ej: Primera Convocatoria - Plazas Rurales")
    
    fecha_hora = models.DateTimeField()
    lugar_o_enlace = models.CharField(max_length=255)
    
    # Estado de esta convocatoria específica
    finalizada = models.BooleanField(default=False)

    class Meta:
        ordering = ['numero_convocatoria']
        unique_together = ['stage', 'numero_convocatoria']

    def save(self, *args, **kwargs):
        # Validación: Solo se pueden agregar convocatorias a etapas tipo ADJUDICACION
        if self.stage.type != StageType.Adjudication:
            raise ValidationError("Solo se pueden crear convocatorias en etapas de Adjudicación.")
        super().save(*args, **kwargs)


# --- User and Authentication Models ---

class User(AbstractUser):
    """
    Usuario personalizado del sistema.
    Extiende AbstractUser de Django y vincula con Person.
    """
    person = models.OneToOneField(
        'Person',
        on_delete=models.CASCADE,
        related_name='user',
        null=True,
        blank=True
    )
    
    # Override username para hacerlo opcional si se desea usar email
    username = models.CharField(max_length=150, unique=True)
    
    # Grupo asignado (solo uno por usuario)
    # ADJUDICATOR, ADMIN, EVALUATOR, NEXUS, TEACHER
    role = models.ForeignKey(
        'Group',
        on_delete=models.PROTECT,
        related_name='users',
        null=True,
        blank=True,
        help_text='Rol del usuario (grupo)'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        if self.person:
            return f"{self.username} - {self.person}"
        return self.username
    
    def get_full_name(self):
        if self.person:
            return f"{self.person.first_name} {self.person.paternal_surname} {self.person.maternal_surname}"
        return self.username


class TeacherProfile(models.Model):
    """
    Perfil específico para usuarios con rol TEACHER.
    Un docente tiene asignado UNA modalidad, UN nivel y UN área curricular.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        primary_key=True
    )
    modality = models.ForeignKey(
        'Modality',
        on_delete=models.PROTECT,
        related_name='teachers',
        help_text='Modalidad asignada al docente'
    )
    level = models.ForeignKey(
        'Level',
        on_delete=models.PROTECT,
        related_name='teachers',
        help_text='Nivel asignado al docente'
    )
    curricular_area = models.ForeignKey(
        'CurricularArea',
        on_delete=models.PROTECT,
        related_name='teachers',
        help_text='Área curricular asignada al docente'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_teacher_profile'
        verbose_name = 'Perfil de Docente'
        verbose_name_plural = 'Perfiles de Docentes'
    
    def __str__(self):
        return f"{self.user.username} - {self.modality.abbreviature} {self.level.name} {self.curricular_area.name}"


class EvaluatorProfile(models.Model):
    """
    Perfil específico para usuarios con rol EVALUATOR.
    Un evaluador puede tener asignadas VARIAS modalidades, niveles y áreas curriculares.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='evaluator_profile',
        primary_key=True
    )
    modalities = models.ManyToManyField(
        'Modality',
        related_name='evaluators',
        help_text='Modalidades asignadas al evaluador'
    )
    levels = models.ManyToManyField(
        'Level',
        related_name='evaluators',
        help_text='Niveles asignados al evaluador'
    )
    curricular_areas = models.ManyToManyField(
        'CurricularArea',
        related_name='evaluators',
        help_text='Áreas curriculares asignadas al evaluador'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_evaluator_profile'
        verbose_name = 'Perfil de Evaluador'
        verbose_name_plural = 'Perfiles de Evaluadores'
    
    def __str__(self):
        return f"{self.user.username} - Evaluador"


# --- Phase Models ---
class Phase(models.Model):
    """
    Fase del proceso de contratación docente basada en Resultados de la Prueba Nacional
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    year = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_phase'
        verbose_name = 'Fase'
        verbose_name_plural = 'Fases'
        ordering = ['-year', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.year})"


class PhaseStage(models.Model):
    """
    Etapas dentro de una fase con sus fechas de inicio y fin
    """
    STAGE_TYPES = [
        ('PUBLICATION', 'Publicación de las vacantes'),
        ('ACCREDITATION', 'Presentación de acreditación de requisitos'),
        ('TIE_EVALUATION', 'Evaluación de expedientes en caso de empate'),
        ('PRELIMINARY_RESULTS', 'Publicación de resultados preliminares'),
        ('CLAIMS', 'Presentación de reclamos'),
        ('CLAIM_RESOLUTION', 'Absolución de reclamos'),
        ('FINAL_RESULTS', 'Publicación de cuadro de mérito final'),
    ]
    
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name='stages')
    stage_type = models.CharField(max_length=30, choices=STAGE_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    class Meta:
        db_table = 'api_phase_stage'
        verbose_name = 'Etapa de Fase'
        verbose_name_plural = 'Etapas de Fases'
        unique_together = ('phase', 'stage_type')
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.phase.name} - {self.get_stage_type_display()}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin')


class PhaseAssignment(models.Model):
    """
    Convocatorias de adjudicación dentro de una fase
    """
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name='assignments')
    assignment_datetime = models.DateTimeField()
    modality = models.ForeignKey('Modality', on_delete=models.PROTECT)
    level = models.ForeignKey('Level', on_delete=models.PROTECT)
    curricular_area = models.ForeignKey('CurricularArea', on_delete=models.PROTECT, null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'api_phase_assignment'
        verbose_name = 'Adjudicación de Fase'
        verbose_name_plural = 'Adjudicaciones de Fases'
        ordering = ['assignment_datetime']
    
    def __str__(self):
        area = f" - {self.curricular_area.name}" if self.curricular_area else ""
        return f"{self.phase.name} - {self.modality.name} - {self.level.name}{area} ({self.assignment_datetime.strftime('%d/%m/%Y %H:%M')})"


# --- Vacancy Management Models ---

class EducationalInstitution(models.Model):
    """
    Institución Educativa (IE)
    """
    code = models.CharField(max_length=20, unique=True, null=True, blank=True, help_text='Código modular de la IE')
    name = models.CharField(max_length=255)
    modality = models.ForeignKey('Modality', on_delete=models.PROTECT)
    level = models.ForeignKey('Level', on_delete=models.PROTECT)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        db_table = 'api_educational_institution'
        verbose_name = 'Institución Educativa'
        verbose_name_plural = 'Instituciones Educativas'
        ordering = ['code']
        unique_together = ['name', 'modality', 'level']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Vacancy(models.Model):
    """
    Vacante asociada a una IE y a una fase
    """
    POSITION_CHOICES = [
        ('DOCENTE', 'Docente'),
        ('AUXILIAR', 'Auxiliar de Educación'),
    ]
    
    VACANCY_TYPE_CHOICES = [
        ('ORGANICA', 'Orgánica'),
        ('EVENTUAL', 'Eventual'),
    ]
    
    VACANCY_REASON_CHOICES = [
        ('LICENCIA', 'Licencia'),
        ('DESTAQUE', 'Destaque'),
        ('ENCARGATURA', 'Encargatura'),
        ('NUEVA_PLAZA', 'Nueva Plaza'),
        ('REASIGNACION', 'Reasignación'),
        ('OTRO', 'Otro'),
    ]
    
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name='vacancies', null=True)
    educational_institution = models.ForeignKey(EducationalInstitution, on_delete=models.CASCADE, related_name='vacancies', null=True)
    
    nexus_code = models.CharField(max_length=50, unique=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, null=True)
    vacancy_type = models.CharField(max_length=20, choices=VACANCY_TYPE_CHOICES, null=True)
    vacancy_reason = models.CharField(max_length=30, choices=VACANCY_REASON_CHOICES, null=True)
    curricular_area = models.ForeignKey('CurricularArea', on_delete=models.PROTECT, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        db_table = 'api_vacancy'
        verbose_name = 'Vacante'
        verbose_name_plural = 'Vacantes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nexus_code} - {self.educational_institution.name} - {self.position}"