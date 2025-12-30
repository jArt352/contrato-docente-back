from rest_framework.routers import DefaultRouter

from api.views import (
    ModalityViewSet, LevelViewSet, CurricularAreaViewSet,
    PrelationOrderViewSet, PrelationViewSet, PrelationRequirementViewSet,
    MandatoryDocumentViewSet, GroupViewSet, UserViewSet
)
from api.views.phase import PhaseViewSet, PhaseStageViewSet, PhaseAssignmentViewSet
from api.views.vacancy import EducationalInstitutionViewSet, VacancyViewSet

router = DefaultRouter()
router.register(r'modalities', ModalityViewSet, basename='modality')
router.register(r'levels', LevelViewSet, basename='level')
router.register(r'curricular-areas', CurricularAreaViewSet, basename='curricular-area')
router.register(r'prelation-orders', PrelationOrderViewSet, basename='prelation-order')
router.register(r'prelations', PrelationViewSet, basename='prelation')
router.register(r'prelation-requirements', PrelationRequirementViewSet, basename='prelation-requirement')
router.register(r'mandatory-documents', MandatoryDocumentViewSet, basename='mandatory-document')

# Phase endpoints
router.register(r'phases', PhaseViewSet, basename='phase')
router.register(r'phase-stages', PhaseStageViewSet, basename='phase-stage')
router.register(r'phase-assignments', PhaseAssignmentViewSet, basename='phase-assignment')

# Vacancy endpoints
router.register(r'educational-institutions', EducationalInstitutionViewSet, basename='educational-institution')
router.register(r'vacancies', VacancyViewSet, basename='vacancy')

# Auth endpoints
router.register(r'auth/groups', GroupViewSet, basename='group')
router.register(r'auth/users', UserViewSet, basename='user')

