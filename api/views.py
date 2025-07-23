from rest_framework import viewsets, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import Animal, Order
from .serializers import (
    AnimalSerializer,
    OrderReadSerializer, OrderWriteSerializer,
    UserSerializer,
    UserRegistrationSerializer
)
from .permissions import IsFarmerOrReadOnly, IsOwnerOrAdmin
from . import mpesa_api

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Or [permissions.IsAdminUser] if you prefer


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer


class MakePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        phone_number = request.data.get('phone_number')

        try:
            order = Order.objects.prefetch_related('items__animal').get(id=order_id, buyer=request.user)
            amount = sum(item.animal.price * item.quantity for item in order.items.all())
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not phone_number:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if order.status != Order.OrderStatus.CONFIRMED:
            return Response({'error': f'Order cannot be paid for in its current state ({order.status}).'}, status=status.HTTP_400_BAD_REQUEST)

        response_data = mpesa_api.initiate_stk_push(phone_number, int(amount), order_id)
        return Response(response_data)


class MpesaCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        stk_callback = data.get('Body', {}).get('stkCallback', {})
        result_code = stk_callback.get('ResultCode')

        if result_code == 0:
            metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            order_id = None
            for item in metadata:
                if item['Name'] == 'AccountReference':
                    order_id = item['Value']
                    break

            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    if order.status == Order.OrderStatus.CONFIRMED:
                        order.status = Order.OrderStatus.PAID
                        order.save()
                except Order.DoesNotExist:
                    pass
        return Response({'status': 'ok'})


class AnimalViewSet(viewsets.ModelViewSet):
    queryset = Animal.objects.filter(is_sold=False).order_by('-created_at')
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        animal_type = self.request.query_params.get('type')
        breed = self.request.query_params.get('breed')
        if animal_type:
            queryset = queryset.filter(animal_type__iexact=animal_type)
        if breed:
            queryset = queryset.filter(breed__icontains=breed)
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OrderWriteSerializer
        return OrderReadSerializer

    def get_queryset(self):
        queryset = Order.objects.prefetch_related('items__animal')
        if self.request.user.is_staff:
            return queryset.all()

        if self.request.user.user_type == self.request.user.Types.FARMER:
            return queryset.filter(items__animal__farmer=self.request.user).distinct()

        return queryset.filter(buyer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user, status=Order.OrderStatus.PENDING)
