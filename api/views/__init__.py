
from .modality import ModalityViewSet
from .level import LevelViewSet
from .curricular_area import CurricularAreaViewSet
from .prelation_order import PrelationOrderViewSet
from .prelation import PrelationViewSet
from .prelation_requirement import PrelationRequirementViewSet
from .mandatory_document import MandatoryDocumentViewSet
from .user import GroupViewSet, UserViewSet
from .auth import CustomTokenObtainPairView, change_password, me

__all__ = [
    'ModalityViewSet',
    'LevelViewSet',
    'CurricularAreaViewSet',
    'PrelationOrderViewSet',
    'PrelationViewSet',
    'PrelationRequirementViewSet',
    'MandatoryDocumentViewSet',
    'GroupViewSet',
    'UserViewSet',
    'CustomTokenObtainPairView',
    'change_password',
    'me',
]
