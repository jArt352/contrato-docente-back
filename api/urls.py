from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .router import router
from .views.auth import CustomTokenObtainPairView, change_password, me

urlpatterns = [
    # Autenticación JWT
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', change_password, name='change_password'),
    path('auth/me/', me, name='me'),
    
    # Router endpoints
    path('', include(router.urls)),
]
