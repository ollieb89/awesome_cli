from django.urls import path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from .api_views import ItemViewSet
from .api_views_crypto import AssetViewSet  # Import the new viewset

router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'assets', AssetViewSet, basename='asset')

urlpatterns = router.urls + [
    # OpenAPI Schema
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
