# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnimalViewSet,
    OrderViewSet,
    MakePaymentView,
    MpesaCallbackView,
    UserProfileView,
    UserViewSet,
    RegisterUserView  # 👈 Import RegisterUserView
)

router = DefaultRouter()
router.register(r'animals', AnimalViewSet, basename='animal')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'users', UserViewSet, basename='user')  # 👈 Add this

urlpatterns = [
    path('', include(router.urls)),
    path('make-payment/', MakePaymentView.as_view(), name='make-payment'),
    path('mpesa-callback/', MpesaCallbackView.as_view(), name='mpesa-callback'),
    path('users/me/', UserProfileView.as_view(), name='get-current-user'),
    path('register/', RegisterUserView.as_view(), name='register'),
]
