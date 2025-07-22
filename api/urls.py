from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnimalViewSet,
    OrderViewSet,
    MakePaymentView,
    MpesaCallbackView,
    CurrentUserView
)

router = DefaultRouter()
router.register(r'animals', AnimalViewSet, basename='animal')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('make-payment/', MakePaymentView.as_view(), name='make-payment'),
    path('mpesa-callback/', MpesaCallbackView.as_view(), name='mpesa-callback'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
]
