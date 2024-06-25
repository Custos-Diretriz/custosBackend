from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LegalAgreementViewSet

router = DefaultRouter()
router.register(r'agreement', LegalAgreementViewSet, basename='legalagreement')

urlpatterns = [
    path('', include(router.urls)),
    path('agreement/<str:access_token>/', LegalAgreementViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='legalagreement-detail'),
    path('agreement/by_party/', LegalAgreementViewSet.as_view({'get': 'by_party'}), name='legalagreement-by-party'),
]
