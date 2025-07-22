# In your Django backend's api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnimalViewSet,
    OrderViewSet,
    MakePaymentView,
    MpesaCallbackView,
    UserProfileView, 
)

router = DefaultRouter()
router.register(r'animals', AnimalViewSet, basename='animal')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('make-payment/', MakePaymentView.as_view(), name='make-payment'),
    path('mpesa-callback/', MpesaCallbackView.as_view(), name='mpesa-callback'),
    
    # === ADD THIS NEW ROUTE FOR USER PROFILE ===
    path('users/me/', UserProfileView.as_view(), name='get-current-user'), 
    # This maps the URL /api/users/me/ to your UserProfileView
]