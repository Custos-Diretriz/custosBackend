from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LegalAgreementViewSet

router = DefaultRouter()
router.register(r'agreement', LegalAgreementViewSet, basename='legalagreement')

urlpatterns = [
    path('', include(router.urls)),
    path('agreement/by_party/', LegalAgreementViewSet.as_view({'get': 'by_party'}), name='legalagreement-by-party'),
]
